from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from cassandra.cluster import Cluster

from .models import *

from .utilities.functions import insert_data, create_tree_view, select_by, update_data, delete_data

import json, random



contact_points = ['localhost']
cluster = Cluster(contact_points)
session = cluster.connect()
keyspace_query = "CREATE KEYSPACE IF NOT EXISTS tfm WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
session.execute(keyspace_query)
session.set_keyspace('tfm')
aux = session.execute("describe tables")

nav_items = []

# Itera sobre los resultados y guarda los valores de la columna 'name' en el array
for row in aux:
    nav_items.append(row.name)

def index(request):

    try:
        select_query = "describe tables"
        result = session.execute(select_query)

        print(result.current_rows)

        columns = result.column_names
        rows = result.all()

        data = {
            'columnNames': columns,
            'rowData': [dict(zip(columns, row)) for row in rows]
        }

        # Renderiza la plantilla con los datos JSON
        return render(request, "index.html", {'data': data, 'nav_items':nav_items})

    except Exception as e:
        print(f"Ha ocurrido un error: {str(e)}")
        # Maneja el error adecuadamente, puedes regresar un JsonResponse si lo prefieres
        return render(request, "error.html", {'error_message': 'Error en la consulta a la base de datos.'})


def tabla(request, item=None):
    try:
        print("Valor de item:", item)  # Imprimir el valor de item para depurar

        if item:
            # Realizar la consulta a Cassandra
            select_query = "SELECT * FROM {}".format(item)
        else:
            # Si no se proporciona el parámetro 'item', utilizar un valor predeterminado
            select_query = "SELECT * FROM example_dataview"

        result = session.execute(select_query)
        
        first_column_index = 0
        # Procesar los resultados
        columns = result.column_names
        rows = sorted(result.all(), key=lambda row: row[first_column_index])  # Ordenar por la primera columna

        data = {
            'columnNames': columns,
            'rowData': [dict(zip(columns, row)) for row in rows]
        }

        tree_data = json.dumps(create_tree_view(columns, item))

        if len(data['rowData']) > 5:
            random_rows = random.sample(data['rowData'], 5)
        else:
            random_rows = data['rowData']

        busqueda_realizada = False

        if 'columna' in request.GET and 'valor' in request.GET:
            columna = request.GET['columna']
            print(columna)
            try:
                valor = int(request.GET['valor'])
                print(valor)
            except ValueError:
                valor = None

            # Verificar si hay un valor proporcionado
            if valor is not None:
                resultados = select_by(item, columna, valor)
                data['rowData'] = [dict(zip(columns, row)) for row in resultados]
                busqueda_realizada = True

        # Renderiza la plantilla con los datos JSON
        return render(request, "tabla.html", {'data': data, 'tree_data': tree_data, 'nav_items':nav_items, 'item': item,'random_rows': random_rows, 'busqueda_realizada': busqueda_realizada})

    except Exception as e:
        print(f"Ha ocurrido un error: {str(e)}")
        # Maneja el error adecuadamente, puedes regresar un JsonResponse si lo prefieres
        return render(request, "error.html", {'error_message': 'Error en la consulta a la base de datos.'})


def telecomando(request):
    success_message = "Los datos se han enviado correctamente a la base de datos."
    error_message = "Ha ocurrido un error, compruebe que ha introducido los datos correctamente"


    try:
        # Realizar la consulta a Cassandra
        select_query = "SELECT * FROM example_dataview"
        result = session.execute(select_query)

        # Procesar los resultados
        columns = result.column_names
        rows = result.all()

        data = {
            'columnNames': columns,
            'rowData': [dict(zip(columns, row)) for row in rows]
        }

        if request.method == 'POST':
            form = tcForm(request.POST)
            if form.is_valid():
                insert_data(form.cleaned_data)
                print(f"Los datos son válidos y se ha enviado a la DB")
                return render(request, "telecomando.html", {'data': data, 'nav_items':nav_items,'success_message': success_message})
            else:
                print(f"No son validos los datos")
                return render(request, "telecomando.html", {'data': data, 'nav_items':nav_items,'form': form, 'error_message': error_message})
        else :
            form = tcForm()
            return render(request, "telecomando.html", {'data': data, 'nav_items':nav_items})

    except Exception as e:
        print(f"Ha ocurrido un error: {str(e)}")
        # Maneja el error adecuadamente, puedes regresar un JsonResponse si lo prefieres
        return render(request, "error.html", {'error_message': 'Error en la consulta a la base de datos.'})

def update(request):
 # Imprimir el valor de item para depurar
    return render(request, "update.html", {'nav_items':nav_items})


def modificar_tabla(request):
    if 'tabla' in request.GET:
        tabla_seleccionada = request.GET['tabla']

        select_query = "SELECT column_name FROM system_schema.columns WHERE keyspace_name = 'tfm' AND table_name = '{}';".format(tabla_seleccionada)
        result = session.execute(select_query)
        columns = [row.column_name for row in result]

        if request.method == 'POST':
            column = request.POST['column']
            new_column = request.POST['new_column']
            try:
                value = int(request.POST['value'])
                new_value = int(request.POST['new_value'])
            except ValueError:
                # Maneja el caso en el que los valores no puedan ser convertidos a enteros
                return HttpResponse("Los valores no son correctos")

            update_data(tabla_seleccionada,column,value,new_column,new_value)


        
        return render(request, 'modificar_tabla.html', {'nav_items':nav_items, 'tabla_seleccionada': tabla_seleccionada, "columns" :columns})
    else:
        # Manejar el caso donde no se seleccionó ninguna tabla
        return HttpResponse("No se seleccionó ninguna tabla.")

def delete(request):
 # Imprimir el valor de item para depurar
    return render(request, "delete.html", {'nav_items':nav_items})

def borrar_datos(request):
    if 'tabla' in request.GET:
        tabla_seleccionada = request.GET['tabla']

        select_query = "SELECT column_name FROM system_schema.columns WHERE keyspace_name = 'tfm' AND table_name = '{}';".format(tabla_seleccionada)
        result = session.execute(select_query)
        columns = [row.column_name for row in result]

        if request.method == 'POST':
            column = request.POST['column']
            try:
                value = int(request.POST['value'])
            except ValueError:
                # Maneja el caso en el que los valores no puedan ser convertidos a enteros
                return HttpResponse("Los valores no son correctos")
        
            delete_data(tabla_seleccionada, column, value)
        
        return render(request, 'borrar_datos.html', {'nav_items':nav_items, 'tabla_seleccionada': tabla_seleccionada, "columns" :columns})
    else:
        # Manejar el caso donde no se seleccionó ninguna tabla
        return HttpResponse("No se seleccionó ninguna tabla.")
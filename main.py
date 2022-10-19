import eel
import pandas as pd
import json
from bson.json_util import dumps # converts mongodb cursor into python suitable 
from bson.son import SON
import glob
import os
from pymongo import MongoClient # pip install "pymongo[srv]"
from bson.objectid import ObjectId #mongodb objectid
from datetime import datetime
import csv
import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import requests #pip install requests
from requests.structures import CaseInsensitiveDict
from geopy.geocoders import Nominatim # pip install geopy
from MLModel import ML_Model
import chart_studio
import plotly.express as px
# pip install -U kaleido
import chart_studio.plotly as py
import plotly.graph_objects as go
import numpy as np
from re import search
from pprint import pprint


db_object = None
machine_learning = None


def pd_to_json(df):
    """helper function, converts python dataframe to json-formatted string"""
    result = df.to_json(orient="index")
    parsed = json.loads(result)
    return parsed

def get_db():
    """helper function, returns the resale price table as an object to run operations (like querying) on"""
    global db_object
    if db_object is None:
        PATH = os.getcwd() + '\\data\\'
        CONNECTION_STR = ""
        with open(PATH + '/access_url.txt', 'r') as f:
            CONNECTION_STR = f.readline()
        print(CONNECTION_STR)
        initial_time = datetime.now()
        client = MongoClient(CONNECTION_STR)
        print(f"Connected to MongoDB client in {(datetime.now() - initial_time).total_seconds()}")
        db = client.test
        db_object = db["resale_prices"]

    return db_object


def get_csv_as_pd():
    """helper function, converts all data rows in all csv files in the "data" folder into a single python dataframe"""
    path = os.getcwd() + '\\data\\cleaned\\'
    print(f"CWD:{path}")
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    return df


def pie_chart_of_column(column_name, quantity_name, graph_title, filter_query = None):
    """returns a pie chart showing the count (and therefore percentage) of all unique values of an input column name.
    add second argument to apply $match filter on target column. filter_query should match .find() filter dictionary format"""
    db = get_db()
    pipeline = [
        {"$unwind": '$' + column_name},
        {"$group": {"_id": '$' + column_name, "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])}
    ] # https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

    if filter_query:
        pipeline.insert(0, {"$match": filter_query})

    initial_time = datetime.now()
    print("querying")
    result = pd.DataFrame(list(db.aggregate(pipeline)))
    print(f"Results retrieved in {(datetime.now() - initial_time).total_seconds()}")
    print(result)
    result = result.rename(columns={"_id": column_name, "count": quantity_name})
    your_labels = result[column_name]
    your_values = result[quantity_name]

    print("Generating graph")
    fig = px.pie(result, values = your_values, names = your_labels, title = graph_title)
    return fig


#     not feasible: data size too large to upload to chart studio unless i pay
# def trend_line_graph(date_column_name, y_column_name, earliest_year, filter_query):
#     db = get_db()
#     cursor = db.find(filter_query)
#     df = pd.DataFrame(list(cursor))
#     # new_df = df[]
#     df = df[[date_column_name, y_column_name]]
#     x_axis = pd.to_datetime(df[date_column_name])
#     y_axis = df[y_column_name]
#     print(df)
#     fig = go.Figure()
#     fig = fig.add_trace(go.Scatter(x=x_axis, y=y_axis))
#     fig = px.line(df, x=x_axis, y=y_axis, title=f"Trend of {y_column_name} since {earliest_year} with range slider and selectors")
#     return fig


def historic_line_graph(x_column_name, y_columnm_name, filter_column, graph_title, filter_query):
    """'x_column_name' and 'y_column_name' define the names of the columns which will have their values 
    assigned to the x and y axis of the line graph respectively"""
    db = get_db()
    print(filter_query)
    cursor = db.find(filter_query)
    df = pd.DataFrame(list(cursor))
    print(df)
    df = df[[x_column_name, y_columnm_name, filter_column]]
    fig = px.line(df, x = x_column_name, y = y_columnm_name, color = filter_column, title=graph_title)
    return fig


def sum_line_graph_by_columns(groupby_column_name_list, x_name, y_name, graph_title, filter_query):
    db = get_db()
    cursor = db.find(filter_query)
    df = pd.DataFrame(list(cursor))
    sales_total = df.groupby(groupby_column_name_list).sum().reset_index()
    linetotal = px.line(sales_total, x = x_name, y = y_name, color = 'flat_type', title=graph_title)
    return linetotal


def aggregated_bar_graph(qty_name, pipeline_list, graph_title):

    db = get_db()
    if not any("$sort" in d for d in pipeline_list):
        pipeline_list.append({"$sort": SON([("count", -1), ("_id", -1)])})
    
    result = pd.DataFrame(list(db.aggregate(pipeline_list)))
    your_labels = result["_id"]
    your_values = result[qty_name]

    # fig = px.bar(result, values = your_values, names = your_labels, title = graph_title)
    fig = px.bar(result, x = your_labels, y = your_values, title = graph_title, orientation = 'v', height = 400)
    return fig


@eel.expose
def query_graphs(input_dict):
    
    # input_dict format should be { "graph_category" : "_____", 0 : {values}, 1 : {values} }
    # where the number corresponsds to which graphs to plot and generate URLs for
    print("Querying graphs")
    print(input_dict)
    output_dict = {}
    # earliest_year = input_dict["month_earliest"].split("_")[0]
    # latest_year = input_dict["month_latest"].split("_")[0]
    if input_dict["graph_category"] == "pie_chart":

        if '0' in input_dict:
            distinct_val_count_column = "flat_model"
            qty_label = "number_of_flats_sold"
            graph_title = "Flat models sold since 1990"
            fig = pie_chart_of_column(distinct_val_count_column, qty_label, graph_title)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(title_font_size = 30)
            print("Uploading graph")
            # url = py.plot(fig, filename = f'{distinct_val_count_column}_distinct_count', auto_open=False)
            filename = input_dict["graph_category"] + "_0"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url

        if '1' in input_dict:
            earliest_year = input_dict['1']["month_earliest"].split("_")[0]
            distinct_val_count_column = "flat_type"
            qty_label = "number_of_flat_type_sold"
            target_town = input_dict['1']["target_town"]
            graph_title = f"Flat type sold in {target_town} since {str(earliest_year)}"
            filter_query = { "$and" : [ { "month" : {"$gte": str(earliest_year) + "-01"}}, { "town" : {"$eq": target_town}} ] }
            fig = pie_chart_of_column(distinct_val_count_column, qty_label, graph_title, filter_query)
            fig.update_layout(
                updatemenus = [
                    {
                        "buttons" : [
                            {
                                "args" : ["type", "pie"],
                                "label" : "Pie Chart",
                                "method" : "restyle"
                            },
                            {
                                "args" : ["type", "bar"],
                                "label" : "Bar Graph",
                                "method" : "restyle"
                            }

                        ],
                        "direction" : "down",
                        "pad" : {"r": 10, "t": 10},
                        "showactive" : True,
                        "x" : 0,
                        "xanchor" : "left",
                        "y" : 1.135,
                        "yanchor" : "top"
                    },
                ],
                title_font_size = 25
            )
            fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
            print("Uploading graph")
            # url = py.plot(fig, filename = f'{distinct_val_count_column}_distinct_count', auto_open=False)
            filename = input_dict["graph_category"] + "_1"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url

    elif input_dict["graph_category"] == "trends":

        if '0' in input_dict:
            earliest_year = input_dict['0']["month_earliest"].split("_")[0]
            x_column_name = "month"
            y_columnm_name = "resale_price"
            filter_column = "flat_type"
            filter_value = input_dict['0']["target_flat_type"]
            target_town = input_dict['0']["target_town"]
            filter_query = { "$and" : [ 
                { "month" : {"$gte": str(earliest_year) + "-01"}}, 
                { "town" : {"$eq": target_town}},
                { filter_column : {"$eq": filter_value}}
                ] }
            graph_title = f"Resale prices of {filter_value} flats"
            fig = historic_line_graph(x_column_name, y_columnm_name, filter_column, graph_title, filter_query)
            fig.update_layout(xaxis_title = "Year", yaxis_title = "Resale Prices")
            fig.update_layout(
                xaxis={
                    "rangeselector" : {
                        "buttons" : [
                            {"count" : 1,
                                "label" : "1m",
                                "step" : "month",
                                "stepmode" : "backward"},
                            {"count" : 6,
                                "label" : "6m",
                                "step" : "month",
                                "stepmode" : "backward"},
                            {"count" : 1,
                                "label" : "Current year to latest date",
                                "step" : "year",
                                "stepmode" : "todate"},
                            {"count" : 1,
                                "label" : "1y",
                                "step" : "year",
                                "stepmode" : "backward"},
                            {"count" : 3,
                                "label" : "Past 3 years",
                                "step" : "year",
                                "stepmode" : "backward"},
                            {"step" : "all"}
                        ]
                    },
                    "rangeslider" : {
                        "visible" : True
                    },
                    "type" : "date"
                }
            )
            # url = py.plot(fig, filename = f'historic_line_graph_by_{filter_column}:{filter_value}', auto_open=False)
            # output_dict[input_dict["graph_category"] + "_0"] = url
            filename = input_dict["graph_category"] + "_0"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url
            

        if '1' in input_dict:
            earliest_year = input_dict['1']["month_earliest"].split("_")[0]
            groupby_column_name_list = ['month','flat_type']
            x_name = "month"
            y_name = "resale_price" 
            target_town = input_dict['1']["target_town"]
            graph_title = f'Total sales of HDB flats transacted in {target_town}'
            filter_query = { "$and" : [ { "month" : {"$gte": str(earliest_year) + "-01"}}, { "town" : {"$eq": target_town}} ] }
            fig = sum_line_graph_by_columns(groupby_column_name_list, x_name, y_name, graph_title, filter_query)
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Sales (in SGD)",
                xaxis = {
                    "rangeselector" : {
                        "buttons" : [
                            {"count" : 1,
                                "label" : "1m",
                                "step" : "month",
                                "stepmode" : "backward"},
                            {"count" : 6,
                                "label" : "6m",
                                "step" : "month",
                                "stepmode" : "backward"},
                            {"count" : 1,
                                "label" : "Current year to latest date",
                                "step" : "year",
                                "stepmode" : "todate"},
                            {"count" : 1,
                                "label" : "1y",
                                "step" : "year",
                                "stepmode" : "backward"},
                            {"count" : 3,
                                "label" : "Past 3 years",
                                "step" : "year",
                                "stepmode" : "backward"},
                            {"step" : "all"}
                        ]
                    },
                    "rangeslider" : {
                        "visible" : True
                    },
                    "type" : "date"
                }
                )
            # url = py.plot(fig, filename = f'sum_line_graph_groupby_[{", ".join(groupby_column_name_list)}]', auto_open=False)
            # output_dict[input_dict["graph_category"] + "_1"] = url
            filename = input_dict["graph_category"] + "_1"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url


    elif input_dict["graph_category"] == "bar_graph":

        if '0' in input_dict:
            category_name = "flat_type"
            pipeline_result = "avg"
            target_town = input_dict['0']["target_town"]
            target_year = int(input_dict['0']["target_year"])
            y_column = "resale_price"
            pipeline_list = [
                {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
                {"$group" : {"_id": "$" + category_name, y_column: {"$" + pipeline_result: "$" + y_column}} }
            ]
            graph_title = f"Average Resale price of the {category_name} in {target_town} on {target_year}"
            fig = aggregated_bar_graph(y_column, pipeline_list, graph_title)
            fig.update_layout(xaxis_title = "Flat Types", yaxis_title = "Average Resale Prices"
            )
            # Add dropdown
            fig.update_layout(
                updatemenus=[
                    {
                        "type" : "buttons",
                        "direction" : "right",
                        "buttons" : [
                            {
                                "args" : ["type", "bar"],
                                "label" : "Bar",
                                "method" : "restyle"
                            },
                            {
                                "args" : ["type", "line"],
                                "label" : "Line",
                                "method" : "restyle"
                            },

                        ],
                        "pad" : {"r": 10, "t": 10},
                        "showactive" : True,
                        "x" : 0,
                        "xanchor" : "left",
                        "y" : 1.9,
                        "yanchor" : "top"
                    },
                ]
            )
            # # Add annotation
            # fig.update_layout(
            #     annotations = [{"text" : 'Ascending order' ,"showarrow" : False,"x" : 0, "y" : 1.1, "yref" : "paper", "align" : "left"}]
            # )
            # url = py.plot(fig, filename = f'avg_resale_price_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
            # output_dict[input_dict["graph_category"] + "_0"] = url
            filename = input_dict["graph_category"] + "_0"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url

        if '1' in input_dict:
            category_name = "flat_type"
            pipeline_result = "sum"
            target_town = input_dict['1']["target_town"]
            target_year = int(input_dict['1']["target_year"])
            pipeline_list = [
                {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
                {"$group" : {"_id": "$" + category_name, pipeline_result: {"$" + pipeline_result: 1}} }
            ]
            graph_title = f"Number of {category_name} sold in {target_town} on {target_year}"
            fig = aggregated_bar_graph(pipeline_result, pipeline_list, graph_title)
            fig.update_layout(xaxis_title="Flat Types", yaxis_title="Number of flat types sold")
            fig.update_layout(
                updatemenus=[
                    {
                        "type" : "buttons",
                        "direction" : "right",
                        "buttons" : [
                            {
                                "args" : ["type", "bar"],
                                "label" : "Bar",
                                "method" : "restyle"
                            },
                            {
                                "args" : ["type", "line"],
                                "label" : "Line",
                                "method" : "restyle"
                            },

                        ],
                        "pad" : {"r": 10, "t": 10},
                        "showactive" : True,
                        "x" : 0,
                        "xanchor" : "left",
                        "y" : 1.9,
                        "yanchor" : "top"
                    },
                ]
            )

            # Add annotation
            fig.update_layout(
                annotations=[{
                    "text" : '' ,
                    "showarrow" : False,
                    "x" : 0, 
                    "y" : 1.1, 
                    "yref" : "paper", 
                    "align" : "left"}
                ]
            )
            # url = py.plot(fig, filename = f'total_number_sold_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
            # output_dict[input_dict["graph_category"] + "_1"] = url
            filename = input_dict["graph_category"] + "_1"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url

        if '2' in input_dict:
            category_name = "flat_type"
            pipeline_result = "sum"
            target_town = input_dict['2']["target_town"]
            target_year = int(input_dict['2']["target_year"])
            y_column = "resale_price"
            pipeline_list = [
                {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
                {"$group" : {"_id": "$" + category_name, pipeline_result: {"$" + pipeline_result: "$" + y_column}} }
            ]
            graph_title = f"Total sales of {category_name} sold in {target_town} on {target_year}"
            fig = aggregated_bar_graph(pipeline_result, pipeline_list, graph_title)
            # Add dropdown
            fig.update_layout(
                updatemenus=[
                    {
                        "type" : "buttons",
                        "direction" : "right",
                        "buttons" : [
                            {
                                "args" : ["type", "bar"],
                                "label" : "Bar",
                                "method" : "restyle"
                            },
                            {
                                "args" : ["type", "line"],
                                "label" : "Line",
                                "method" : "restyle"
                            },

                        ],
                        "pad" : {"r": 10, "t": 10},
                        "showactive" : True,
                        "x" : 0,
                        "xanchor" : "left",
                        "y" : 1.9,
                        "yanchor" : "top"
                    },
                ]
            )
            # Add annotation
            fig.update_layout(
                annotations=[{
                    "text" : '', 
                    "showarrow" : False, 
                    "x" : 0, 
                    "y" : 1.1, 
                    "yref" : "paper", 
                    "align" : "left"}
                ]
            )
            # url = py.plot(fig, filename = f'total_resale_price_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
            # output_dict[input_dict["graph_category"] + "_2"] = url
            filename = input_dict["graph_category"] + "_2"
            url = f"web/images/{filename}.png"
            fig.write_image(url)
            print("Uploaded graph")
            output_dict[filename] = url
        

    else:
        print("Invalid graph category, exiting")
        return None
    print("graphs settled")
    print(output_dict)
    return output_dict


# @eel.expose
# def get_main_graphs():
#     # run all functions to produce graphs here
#     # return a list of iframe URLs
#     earliest_year = datetime.today().year - 5
#     output_dict = {}

#     distinct_val_count_column = "flat_model"
#     qty_label = "number_of_flats_sold"
#     graph_title = "Flat models sold since 1990s"
#     fig = pie_chart_of_column(distinct_val_count_column, qty_label, graph_title)
#     fig.update_traces(textposition='inside', textinfo='percent+label')
#     fig.update_layout(title_font_size = 30)
#     url = py.plot(fig, filename = f'{distinct_val_count_column}_distinct_count', auto_open=False)
#     output_dict[graph_title] = url

#     # date_column_name = "month"
#     # y_column_name = "resale_price"
#     # filter_query = { "$and" : [ { "month" : {"$gte": "2021" + "-01"}} ] }
#     # fig = trend_line_graph(date_column_name, y_column_name, 2021, filter_query)
#     # fig.update_layout(title_text="Trend of resale prices for the past 5 years with range slider and selectors")
#     # fig.update_layout(
#     #     xaxis={
#     #         "rangeselector" : {
#     #             "buttons" : [
#     #                 {"count" : 1,
#     #                     "label" : "1m",
#     #                     "step" : "month",
#     #                     "stepmode" : "backward"},
#     #                 {"count" : 6,
#     #                     "label" : "6m",
#     #                     "step" : "month",
#     #                     "stepmode" : "backward"},
#     #                 {"count" : 1,
#     #                     "label" : "Year to latest date",
#     #                     "step" : "year",
#     #                     "stepmode" : "todate"},
#     #                 {"count" : 1,
#     #                     "label" : "1y",
#     #                     "step" : "year",
#     #                     "stepmode" : "backward"},
#     #                 {"step" : "all"}
#     #             ]
#     #         },
#     #         "rangeslider" : {
#     #             "visible" : True
#     #         },
#     #         "type" : "date"
#     #     }
#     # )
#     # fig.update_layout(
#     #     xaxis_title="Year", yaxis_title="Resale Prices"
#     # )
#     # url = py.plot(fig, filename = f'{y_column_name}_trend', auto_open=False)
#     # output_dict[graph_title] = url
    

#     distinct_val_count_column = "flat_type"
#     qty_label = "number_of_flat_type_sold"
#     target_town = "ANG MO KIO"
#     graph_title = f"Flat type sold in {target_town} since 2017"
#     filter_query = { "$and" : [ { "month" : {"$gte": str(earliest_year) + "-01"}}, { "town" : {"$eq": target_town}} ] }
#     fig = pie_chart_of_column(distinct_val_count_column, qty_label, graph_title, filter_query)
#     fig.update_layout(
#         updatemenus = [
#             {
#                 "buttons" : [
#                     {
#                         "args" : ["type", "pie"],
#                         "label" : "Pie Chart",
#                         "method" : "restyle"
#                     },
#                     {
#                         "args" : ["type", "bar"],
#                         "label" : "Bar Graph",
#                         "method" : "restyle"
#                     }

#                 ],
#                 "direction" : "down",
#                 "pad" : {"r": 10, "t": 10},
#                 "showactive" : True,
#                 "x" : 0,
#                 "xanchor" : "left",
#                 "y" : 1.135,
#                 "yanchor" : "top"
#             },
#         ],
#         title_font_size = 25
#     )
#     fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
#     url = py.plot(fig, filename = f'{distinct_val_count_column}_distinct_count', auto_open=False)
#     output_dict[graph_title] = url

#     x_column_name = "month"
#     y_columnm_name = "resale_price"
#     filter_column = "flat_type"
#     filter_value = "4 ROOM"
#     target_town = "ANG MO KIO"
#     filter_query = { "$and" : [ 
#         { "month" : {"$gte": str(earliest_year) + "-01"}}, 
#         { "town" : {"$eq": target_town}},
#         { filter_column : {"$eq": filter_value}}
#         ] }
#     graph_title = f"Resale prices of {filter_value} flats"
#     fig = historic_line_graph(x_column_name, y_columnm_name, filter_column, graph_title, filter_query)
#     fig.update_layout(xaxis_title = "Year", yaxis_title = "Resale Prices")
#     fig.update_layout(
#         xaxis={
#             "rangeselector" : {
#                 "buttons" : [
#                     {"count" : 1,
#                          "label" : "1m",
#                          "step" : "month",
#                          "stepmode" : "backward"},
#                     {"count" : 6,
#                          "label" : "6m",
#                          "step" : "month",
#                          "stepmode" : "backward"},
#                     {"count" : 1,
#                          "label" : "Current year to latest date",
#                          "step" : "year",
#                          "stepmode" : "todate"},
#                     {"count" : 1,
#                          "label" : "1y",
#                          "step" : "year",
#                          "stepmode" : "backward"},
#                     {"count" : 3,
#                          "label" : "Past 3 years",
#                          "step" : "year",
#                          "stepmode" : "backward"},
#                     {"step" : "all"}
#                 ]
#             },
#             "rangeslider" : {
#                 "visible" : True
#             },
#             "type" : "date"
#         }
#     )
#     url = py.plot(fig, filename = f'historic_line_graph_by_{filter_column}:{filter_value}', auto_open=False)
#     output_dict[graph_title] = url


#     groupby_column_name_list = ['month','flat_type']
#     x_name = "month"
#     y_name = "resale_price" 
#     target_town = "ANG MO KIO"
#     graph_title = f'Total sales of HDB flats transacted in {target_town}'
#     filter_query = { "$and" : [ { "month" : {"$gte": str(earliest_year) + "-01"}}, { "town" : {"$eq": target_town}} ] }
#     fig = sum_line_graph_by_columns(groupby_column_name_list, x_name, y_name, graph_title, filter_query)
#     fig.update_layout(
#         xaxis_title="Year",
#         yaxis_title="Sales (in SGD)",
#         xaxis = {
#             "rangeselector" : {
#                 "buttons" : [
#                     {"count" : 1,
#                          "label" : "1m",
#                          "step" : "month",
#                          "stepmode" : "backward"},
#                     {"count" : 6,
#                          "label" : "6m",
#                          "step" : "month",
#                          "stepmode" : "backward"},
#                     {"count" : 1,
#                          "label" : "Current year to latest date",
#                          "step" : "year",
#                          "stepmode" : "todate"},
#                     {"count" : 1,
#                          "label" : "1y",
#                          "step" : "year",
#                          "stepmode" : "backward"},
#                     {"count" : 3,
#                          "label" : "Past 3 years",
#                          "step" : "year",
#                          "stepmode" : "backward"},
#                     {"step" : "all"}
#                 ]
#             },
#             "rangeslider" : {
#                 "visible" : True
#             },
#             "type" : "date"
#         }
#         )
#     url = py.plot(fig, filename = f'sum_line_graph_groupby_[{", ".join(groupby_column_name_list)}]', auto_open=False)
#     output_dict[graph_title] = url

    
#     category_name = "flat_type"
#     pipeline_result = "avg"
#     target_town = "ANG MO KIO"
#     target_year = 2017
#     y_column = "resale_price"
#     pipeline_list = [
#         {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
#         {"$group" : {"_id": "$" + category_name, y_column: {"$" + pipeline_result: "$" + y_column}} }
#     ]
#     graph_title = f"Average Resale price of the {category_name} in {target_town} on {target_year}"
#     fig = aggregated_bar_graph(y_column, pipeline_list, graph_title)
#     fig.update_layout(xaxis_title = "Flat Types", yaxis_title = "Average Resale Prices"
#     )
#     # Add dropdown
#     fig.update_layout(
#         updatemenus=[
#             {
#                 "type" : "buttons",
#                 "direction" : "right",
#                 "buttons" : [
#                     {
#                         "args" : ["type", "bar"],
#                         "label" : "Bar",
#                         "method" : "restyle"
#                     },
#                       {
#                         "args" : ["type", "line"],
#                         "label" : "Line",
#                         "method" : "restyle"
#                       },

#                 ],
#                 "pad" : {"r": 10, "t": 10},
#                 "showactive" : True,
#                 "x" : 0,
#                 "xanchor" : "left",
#                 "y" : 1.9,
#                 "yanchor" : "top"
#             },
#         ]
#     )
#     # # Add annotation
#     # fig.update_layout(
#     #     annotations = [{"text" : 'Ascending order' ,"showarrow" : False,"x" : 0, "y" : 1.1, "yref" : "paper", "align" : "left"}]
#     # )
#     url = py.plot(fig, filename = f'avg_resale_price_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
#     output_dict[graph_title] = url


#     category_name = "flat_type"
#     pipeline_result = "sum"
#     target_town = "ANG MO KIO"
#     target_year = 2017
#     pipeline_list = [
#         {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
#         {"$group" : {"_id": "$" + category_name, pipeline_result: {"$" + pipeline_result: 1}} }
#     ]
#     graph_title = f"Number of {category_name} sold in {target_town} on {target_year}"
#     fig = aggregated_bar_graph(pipeline_result, pipeline_list, graph_title)
#     fig.update_layout(xaxis_title="Flat Types", yaxis_title="Number of flat types sold")
#     fig.update_layout(
#         updatemenus=[
#             {
#                 "type" : "buttons",
#                 "direction" : "right",
#                 "buttons" : [
#                     {
#                         "args" : ["type", "bar"],
#                         "label" : "Bar",
#                         "method" : "restyle"
#                     },
#                       {
#                         "args" : ["type", "line"],
#                         "label" : "Line",
#                         "method" : "restyle"
#                       },

#                 ],
#                 "pad" : {"r": 10, "t": 10},
#                 "showactive" : True,
#                 "x" : 0,
#                 "xanchor" : "left",
#                 "y" : 1.9,
#                 "yanchor" : "top"
#             },
#         ]
#     )

#     # Add annotation
#     fig.update_layout(
#         annotations=[{
#             "text" : '' ,
#             "showarrow" : False,
#             "x" : 0, 
#             "y" : 1.1, 
#             "yref" : "paper", 
#             "align" : "left"}
#         ]
#     )

#     url = py.plot(fig, filename = f'total_number_sold_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
#     output_dict[graph_title] = url

#     category_name = "flat_type"
#     pipeline_result = "sum"
#     target_town = "ANG MO KIO"
#     target_year = 2017
#     y_column = "resale_price"
#     pipeline_list = [
#         {"$match": {"town": target_town, "month": {"$regex" : str(target_year)}}},
#         {"$group" : {"_id": "$" + category_name, pipeline_result: {"$" + pipeline_result: "$" + y_column}} }
#     ]
#     graph_title = f"Total sales of {category_name} sold in {target_town} on {target_year}"
#     fig = aggregated_bar_graph(pipeline_result, pipeline_list, graph_title)
#     # Add dropdown
#     fig.update_layout(
#         updatemenus=[
#             {
#                 "type" : "buttons",
#                 "direction" : "right",
#                 "buttons" : [
#                     {
#                         "args" : ["type", "bar"],
#                         "label" : "Bar",
#                         "method" : "restyle"
#                     },
#                       {
#                         "args" : ["type", "line"],
#                         "label" : "Line",
#                         "method" : "restyle"
#                       },

#                 ],
#                 "pad" : {"r": 10, "t": 10},
#                 "showactive" : True,
#                 "x" : 0,
#                 "xanchor" : "left",
#                 "y" : 1.9,
#                 "yanchor" : "top"
#             },
#         ]
#     )
#     # Add annotation
#     fig.update_layout(
#         annotations=[{
#             "text" : '', 
#             "showarrow" : False, 
#             "x" : 0, 
#             "y" : 1.1, 
#             "yref" : "paper", 
#             "align" : "left"}
#         ]
#     )
#     url = py.plot(fig, filename = f'total_resale_price_by_{category_name}_in_{target_town}_on_{target_year}', auto_open=False)
#     output_dict[graph_title] = url

#     print(output_dict)
#     return None


@eel.expose
def init_ml_model():
    """Sets the regression model into the global variable"""
    global machine_learning
    if not machine_learning:
        machine_learning = ML_Model()


@eel.expose
def get_predicted_value(input_list):
    global machine_learning
    # note: input_list must must be a list of dictionaries, with each dict representing each row
    df = pd.DataFrame([input_list])
    result = machine_learning.predict_values(df)
    print("The predicted value(s) is/are:")
    print(result)
    return result[0] # result comes out as list


@eel.expose
def get_prediction_graph(input_row, years_ahead):
    global machine_learning
    # note: input_list must must be a list of dictionaries, with each dict representing each row
    months_to_iterate = int(years_ahead) * 12
    e = input_row.copy()
    input_list = [e]
    date_val = input_row["month"].split("-")
    year_val = int(date_val[0])
    month_val = int(date_val[1])

    for i in range(months_to_iterate):
        
        if month_val >= 12:
            year_val += 1
            month_val = 1
        else:
            month_val += 1
        input_row["month"] = str(year_val) + "-" + str(month_val)
        temp_dict = input_row.copy()
        input_list.append(temp_dict)

    date_list = [e["month"] for e in input_list]
    print(f"Date list: {date_list}")
    df = pd.DataFrame(input_list)
    print(df.head(3))
    print(df.tail(3))
    result = machine_learning.predict_values(df)
    print("The predicted value(s) is/are:")
    print(result)
    prediction_graph_df = pd.DataFrame(
        {
            "date" : date_list,
            "predicted_price" : result
        })
    print(prediction_graph_df.head(2))
    print(prediction_graph_df.tail(2))
    print(len(prediction_graph_df.index))
    

    fig = px.line(prediction_graph_df, x='date', y='predicted_price')
    url = py.plot(fig, filename = 'prediction_graph', auto_open=False)
    print(url)
    return url
    # test result output
    # return result[0] # result comes out as list


@eel.expose
def get_dropdown_values(query_mode, column_names = [], query_dict = {}):
    """retrieves all unique data from specified columns in the .csv file containing dataset"""
    output_dict = { "query_mode" : query_mode } # defines whether the dropdown values are for the query input

    year_toggle = False # to set whether to return the full month value, or just year
    year_value_limit = 0  # to set how many years before the latest date to return
    if any("year_limit_" in s for s in column_names):
        # index_to_replace = column_names.index("year")

        for index, column_name in enumerate(column_names):
            if "year_limit_" in column_name:
                year_value_limit = int(column_name.split("_limit_")[1])
                index_to_replace = index

        column_names[index_to_replace] = "month"
        year_toggle = True

    db = get_db()
    if len(column_names) > 0:  # checks if columns were added in the function args 
        initial_time = datetime.now()
        for key in column_names: # for every column name
            distinct_value_list = db.distinct(key, query_dict) # get all distinct values of each column name
            output_dict[key] = distinct_value_list # insert key name with distinct values in dict
        print(f"Done collating unique values in {(datetime.now() - initial_time).total_seconds()}")

        if year_toggle:
            years_list = list({x.split("-")[0] for x in output_dict["month"]})
            output_dict["month"] = sorted(years_list, reverse=True)[:year_value_limit] # get all unique year values

        return output_dict
    else:
        # if no columns were specified, this function is useless
        print("No columns specified in function. Aborting....")
        return None
    # sample result: { flat_type: (7) […], town: (27) […], street_name: (579) […], flat_model: (21) […], month: (393) […] }
    # if len(column_names) > 0:

    #     if input_df == None:
    #         input_df = get_csv_as_pd()

    #     for name in column_names:
    #         if name in input_df.columns:
    #             output_dict[name] = list(input_df[name].unique())
    #         else:
    #             print(f"{name} is not a valid column.\n Column list:{input_df.columns}\n")
    #     return json.loads(json.dumps(output_dict, indent = 4))
    # else:
    #     print("No columns specified in function. Aborting....")
    #     return None
    
# @eel.expose
# def heatmap_plot():
#     #this function is to plot the heatmap to predict the future price of flats based on type of flat and town area
#     #below is just hardcoded example 
#     vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
#               "potato", "wheat", "barley"]
#     farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
#            "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

#     harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
#                     [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
#                     [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
#                     [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
#                     [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
#                     [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
#                     [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


#     fig, ax = plt.subplots()
#     im = ax.imshow(harvest)

#     # Show all ticks and label them with the respective list entries
#     ax.set_xticks(np.arange(len(farmers)), labels=farmers)
#     ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

#     # Rotate the tick labels and set their alignment.
#     plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
#          rotation_mode="anchor")

#     # Loop over data dimensions and create text annotations.
#     for i in range(len(vegetables)):
#         for j in range(len(farmers)):
#             text = ax.text(j, i, harvest[i, j],
#                        ha="center", va="center", color="w")

#     ax.set_title("Harvest of local farmers (in tons/year)")
#     fig.tight_layout()
#     fig.savefig('web/resources/heatmap3.jpg')
#     #plt.show()
#     # return savedfig
    
# @eel.expose
# def query_db_by_id(id_list, result_limit = 2000):


@eel.expose
def query_db(search_query_dict, result_limit = 2000, export = False):
    DATE_COLUMN_NAME = "month"
    ID_COLUMN_NAME = "_id"
    data_table = get_db()
    
    # If we are getting everything, query dict should be an empty dict {}
    # sample query appearance:

    # "$and" : [{
    #                 "center_id" : { "$eq" : 11}
    #             },
    #             {
    #                 "meal_id" : { "$ne" : 1778}
    #             }]
    initial_time = datetime.now()
    if search_query_dict:  
        # if a query dict is specified, the code here runs to filter results
        query_list = []
        pipeline = []
        # search_query_dict format is { column_name : {"search_type": "...", "value": "..."} }
        for key,value in search_query_dict.items():  # for each *column to search* : *search value*
            search_value = value["value"]
            if search_value and "month_" in key: 
                # special condition, if user is trying to set a date filter range
                # column name value will either be month_earliest or month_latest
                if key == "month_earliest":
                    query_list.append({DATE_COLUMN_NAME: {"$gte": search_value}})
                if key == "month_latest":
                    query_list.append({DATE_COLUMN_NAME: {"$lte": search_value}})
            
            elif search_value and "_id" in key:
                # for standardisation, search_value is expected to be a list
                search_value = [ObjectId(x) for x in search_value]
                query_list.append({"_id": {"$in": search_value}})

            elif search_value:
                if value["search_type"] == "match_text":
                    # must match value. Acceptable to use here, since dropdowns take values from the data itself
                    query_list.append({key: {"$eq": search_value}})
                elif value["search_type"] == "number":
                    pipeline = [
                            {"$addFields": { key + '_temp_str' : { '$toString' : '$' + key} }},
                            # {"$match": {"temp_str": f"/{search_value}/"}},
                        ]
                    query_list.append({key + '_temp_str': {"$regex" : f".*{search_value}.*"}})
                    # result = pd.DataFrame(list(data_table.aggregate(pipeline)))
                else:
                    # as a catch-all, if i do not specify the search_type value
                    query_list.append({key: {"$regex" : f".*{search_value}.*"}}) # search if string contains, case insensitive

        # search_query_dict = {})

        if not pipeline:
            print(query_list)
            cursor = data_table.find({"$and" : query_list}, limit=result_limit)
        else:
            pipeline.append({ "$match": {"$and" : query_list} })
            print(pipeline)
            cursor = data_table.aggregate(pipeline)
    else:
        # else, get everything, limit results via result_limit
        cursor = data_table.find({}, limit=result_limit)
    print(f"Query done in {(datetime.now() - initial_time).total_seconds()}")
    

    if export:
        print("Exporting data as CSV")
        initial_time = datetime.now()
        df = pd.DataFrame(list(cursor))
        print(df.info())
        PATH = os.getcwd() + '\\web\\resources\\queryData.csv'
        df.to_csv(PATH)
        print(f"CSV conversion done in {(datetime.now() - initial_time).total_seconds()}")
        return True
    else:
        initial_time = datetime.now()
        cursor = cursor.sort("month", -1)
        result = json.loads(dumps(cursor))
        print(f"JSON conversion done in {(datetime.now() - initial_time).total_seconds()}")
        return result
    
    # 2000
@eel.expose
def csvFormat(data): 
    # usage has been phased out for the main table, but the favourites table still uses this function
    # due to how it operates (in that the source of the data is retrieved from the front end)
    PATH = os.getcwd() + '\\web\\resources\\queryData.csv'
    key = data[0].keys()
    
    with open(PATH + 'queryData.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, key)
        writer.writeheader()
        writer.writerows(data)
        

# @eel.expose
# def query_csv(search_query_dict = None, max_rows = 2000):
#     """retrieves data from .csv file containing dataset. returns data as JSON to allow the Javascript code to handle the data as an object"""
#     df = get_csv_as_pd()

#     if search_query_dict: # if there is a JSON object added into the parameters
#         # https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/ for multiple query method
        
#         print(search_query_dict)
#         # conditions = []
#         for key,value in search_query_dict.items():
#             # conditions.append(df[key].str.contains(value))

#             if value and "month_" in key: # special condition, if user is trying to set a date filter range
#                 if key == "month_earliest":
#                     df = df[df["month"] >= value]
#                 if key == "month_latest":
#                     df = df[df["month"] <= value]
#                 print(f"Filtered. Nuber of rows: {len(df.index)}")

#             elif value and key in df.columns: # if value is not empty, and if column name exists in dataframe
#                 print(key)
#                 print(value)
#                 df = df[df[key].astype(str).str.contains(value)]
#                 print(f"Filtered. Nuber of rows: {len(df.index)}")

            
        
#         # sample search_query_json = {
#         #     "month": "",
#         #     "town": "",
#         #     "flat_type": "",
#         #     "street_name": "",
#         #     "storey_range": "",
#         #     "floor_area_sqm": "",
#         #     "flat_model": "",
#         #     "lease_commencement_date": "",
#         #     "resale_price": "",
#         #     "remaining_lease": ""
#         # }
    
#     print(df["month"].min())
#     print(df["month"].max())
#     df = df.iloc[:max_rows]  # determines max rows shown
    
#     return pd_to_json(df)

@eel.expose
def getPostalCode(streetName, block):
    #initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")

    datatable = get_db()
    

    # datatable = get_db()
    place =str(block)+ "," + streetName
    location = geolocator.geocode(place)

    #traverse the data
    data = location.raw
    loc_data = data['display_name'].split(',')
    loc_data_new = []
    for i in loc_data:
        replaced = i.replace(' ','')
        loc_data_new.append(replaced)
    print(loc_data_new)
    print(loc_data_new[-2])
    return loc_data_new[-2]

#returns the id of the record when user click into it
@eel.expose
def getRecordId(month,town,flat_type,block,street_name,storey_range,floor_area_sqm,flat_model,lease_commence_date,resale_price,remaining_lease):
    data_table = get_db()
    record = data_table.find_one({"month":month, "town":town,"flat_type":flat_type,"block":block,"street_name":street_name,"storey_range":storey_range,"floor_area_sqm":floor_area_sqm,"flat_model":flat_model,"lease_commence_date":lease_commence_date,"resale_price":resale_price,"remaining_lease":remaining_lease})
    return record["_id"]

#get the record details by id
@eel.expose
def getRecordByRecordId(id):
    data_table = get_db()
    # cursor = data_table.find({'_id': id})
    # result = json.loads(dumps(cursor))
    # return result
    record = data_table.find_one({'_id': ObjectId(id) })
    return record

@eel.expose
def getColumns(id):
    print("in getColumns")
    columnlist=[]
    record_dict = getRecordByRecordId(id)
    print(record_dict)
    keylist = list(record_dict.keys())

    for key in keylist:
        if key == "_id":
            continue
        else:
            columnlist.append(key)

    print(columnlist)
    return columnlist

@eel.expose
def getRow(id):
    rowlist=[]
    record_dict = getRecordByRecordId(id)
    print(record_dict)
    keylist = list(record_dict.values())

    for key in keylist:
        rowlist.append(key)

    print(rowlist)
    return rowlist

#get place id
def getPlacesId(postalcode):
    geoapify = "https://api.geoapify.com/v1/geocode/search?postcode="+postalcode+"&apiKey=282342ec9baa42e2ba5897587f10f26c"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp2 = requests.get(geoapify,headers=headers)
    newdict = resp2.json()
    array = newdict['features']
    placeid = ""
    for dict in array:
        properties = dict['properties']

        placeid = properties['place_id']
        # for value in dict['properties']:
        #     print(value)
        
    return placeid


@eel.expose
def getplaces(postalcode,category):
    #print("postalcode in getplaces is: " + postalcode + ",Category is: " + category)
    placeid = getPlacesId(postalcode)
    #print("placeid: " + placeid)
    try:
        geoapify = "https://api.geoapify.com/v2/places?categories="+category+"&filter=place:"+placeid+"&limit=50&apiKey=282342ec9baa42e2ba5897587f10f26c"
        print(geoapify)
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        resp2 = requests.get(geoapify,headers=headers)
        newdict = resp2.json()
        print("printing newdict")
        pprint(newdict)
        items = newdict['features']
        newarray = []
    
        data_dict = {}
        data_list=[]
        for item in items:
            newarray.append(item['properties'])
        for i in newarray:
            print("print i")
            pprint(i)
            data_dict = {}
            name = i['address_line1']
            # raw = i['datasource']['raw']
            # amenity = raw['amenity']
            distance = i['distance']
            postcode = i['postcode']
       
            data_dict['name'] = name
            # data_dict['amenity'] = amenity
            data_dict['distance'] = distance
            data_dict['postcode'] = postcode
            data_list.append(data_dict)
    except requests.exceptions.ConnectionError:
        print('connection error occurred')
    return data_list

if __name__ == "__main__":
    
    eel.init('web', allowed_extensions=['.js', '.html'])
    # mode value depends on preferred browser. should find a way to implement our own browser check
    chart_studio.tools.set_credentials_file(username='tjl081', api_key='3aQmYk1TJQIdiao8Pqip')
    print("main.py running") 
    # Call a Javascript function. the results are queued then displayed the moment the webpage starts up
    eel.start('main.html', mode="chrome-app") # code seems to pause here while website is running.




# we constantly fetch data from the CSV with every user query. while this seems inefficient, it is the only way (i know) to get live data.
# also easier integration when converting to database access


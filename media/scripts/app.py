from pathlib import Path

import pandas

from shiny import reactive
import plotly.express as px
from shiny.express import input, render, ui
import ipyleaflet as ipyl
from shinywidgets import render_widget

# Data
data = reactive.value(pandas.DataFrame())
# data = reactive.value(pandas.read_csv(Path(__file__).parent / "schools_to_check.csv"))

    

## DATA
ui.input_file("file1", "Choose a file to upload:", multiple=False)
ui.input_action_button("rst", "reset", class_="btn-sm")
select = reactive.value(0)


@reactive.calc
def dat():
    if input.file1():
        print("Got FIle",input.file1()[0])
        data.set(pandas.read_csv(input.file1()[0]['datapath']))
    return data.get()


@reactive.calc
def currentRow():
    return data.get().iloc[select.get()]

with ui.navset_card_underline():


    with ui.nav_panel("Data frame"):

        @render.data_frame
        def frame():
            # Give data.get() to render.DataGrid to customize the grid
            f = render.DataGrid(
                data.get().sort_values(by="streetview", ascending=False)[
                    ["Link", "Verificada", "Nome", "streetview"]
                ],
                selection_mode="rows",
            )
            return f

    with ui.nav_panel("Map"):
        @render.ui
        def progress():
            return ui.input_slider("slider", "Slider", 0, dat()['Nome'].size, select.get())

        with ui.layout_columns():
            with ui.card():
                with ui.layout_columns():
                    ui.input_action_button("back", "Anterior", class_="btn-sm")
                    ui.input_action_button("go", "Proxima", class_="btn-sm")
                @render.ui
                def nb():
                    return [ ui.markdown(f"""## {currentRow()[0]}"""),
                            ui.markdown(f"""{currentRow()['Nome']}""")
                           ]
                @render.ui
                def addrs():
                    return ui.markdown(f"""{currentRow()['End']}""")

                @render.ui
                def sv():
                    return ui.markdown(f"""[GoogleMaps]({currentRow()['Link']})""")

            with ui.card():

                @render.ui
                def ctrl():
                    return [
                        
                        ui.input_checkbox_group(  
                            "checkbox_group",  
                            "Checkbox group",  
                            {  
                                "end": "Endereco incorreto",  
                                "name": "Nome Discrepante",  
                            },  
                        ),  

                        ui.input_switch(
                            "resp",
                            "Verificado",
                            value=currentRow()["Verificada"] == "S",
                        ),
                        ui.input_text(
                            "respons", "Responsavel", value=currentRow()["Respons"]
                        ),
                        ui.input_text(
                            "lat", "Latitude, Longitude", value=f"{currentRow()["Lat"]}, {currentRow()["Long"]}"
                        ),
                        ui.input_action_button("save", "Salvar", class_="btn-primary"),
                    ]

        with ui.card():

            @render_widget
            def map():

                if pandas.isna(currentRow()["Lat"]):
                    return
                m = ipyl.Map(
                    center=(currentRow()["Lat"], currentRow()["Long"]),
                    zoom=15,
                    basemap=ipyl.basemaps.OpenStreetMap.Mapnik,
                )
                m.add_layer(ipyl.Marker(location=m.center, draggable=False))
                return m

        with ui.layout_columns():

            @render.download(label="Download CSV")
            def download1():
                """
                This is the simplest case. The implementation simply returns the name of a file.
                Note that the function name (`download1`) determines which download_button()
                corresponds to this function.
                """
                path = Path(__file__).parent / input.file1()[0]['name']
                data.get().to_csv(path, index=False)
                return str(path)


# Reactions
def save():
    d = data.get()
    d.loc[select.get(), "Verificada"] = "S" if input.resp.get() else "N"
    d.loc[select.get(), "Respons"] = input.respons.get()
    lat, long = input.lat.get().split(", ")
    print(lat,long)
    
    d.loc[select.get(), "Lat"] = lat
    d.loc[select.get(), "Long"] = long
    
    # d.loc[select.get(), "Errors"] = 
    # print(select.get(), currentRow()[['Errors', 'Nome']])
    print(d)
    data.set(d)
    
@reactive.effect
@reactive.event(input.save, ignore_none=False)
def x():
    save()


@reactive.effect
@reactive.event(input.go, ignore_none=False)
def go_map():
    select.set(select.get() + 1)
    frame.cell_selection()["rows"] = select



@reactive.effect
@reactive.event(input.back, ignore_none=False)
def back_map():
    select.set(select.get() - 1)
    frame.cell_selection()["rows"] = select

@reactive.effect
@reactive.event(input.slider, ignore_none=False)
def sld():
    select.set(input.slider.get())
    frame.cell_selection()["rows"] = select

@reactive.effect
@reactive.event(input.rst, ignore_none=False)
def y():
    dat()

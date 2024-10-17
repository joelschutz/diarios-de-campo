from pathlib import Path

import pandas

from shiny import reactive
from shiny.express import input, render, ui
import ipyleaflet as ipyl
from shinywidgets import render_widget


data = pandas.read_csv(Path(__file__).parent / "links (1).csv")
select = reactive.value(0)


@reactive.calc
def dat():
    return data


@reactive.calc
def currentRow():
    return data.iloc[select.get()]


with ui.navset_card_underline():

    with ui.nav_panel("Data frame"):

        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            f = render.DataGrid(
                dat().sort_values(by="streetview", ascending=False)[
                    ["Link", "Verificada", "Nome", "streetview"]
                ],
                selection_mode="rows",
            )
            return f

    with ui.nav_panel("Map"):

        with ui.layout_columns():
            with ui.card():
                with ui.layout_columns():
                    ui.input_action_button("back", "Anterior", class_="btn-sm")
                    ui.input_action_button("go", "Proxima", class_="btn-sm")

                @render.ui
                def name():
                    return f"""{currentRow()['Nome']} - {currentRow()[0]}"""

                @render.ui
                def sv():
                    return ui.markdown(f"""[GoogleMaps]({currentRow()['Link']})""")

            with ui.card():

                @render.ui
                def ctrl():
                    return [
                        ui.input_switch(
                            "resp", "Verificado", value=currentRow()["Verificada"] == 'S'
                        ),
                        ui.input_text(
                            "respons", "Responsavel", value=currentRow()["Respons"]
                        ),
                    ]

        with ui.card():

            @render_widget
            def map():
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
                path = Path(__file__).parent / "links (1).csv"
                data.to_csv(path, index=False)
                return str(path)

            ui.input_action_button("save", "Salvar", class_="btn-primary")


@reactive.effect
@reactive.event(input.go, ignore_none=False)
def go_map():
    print(select.get())
    select.set(select.get() + 1)
    frame.cell_selection()["rows"] = select


@reactive.effect
@reactive.event(input.back, ignore_none=False)
def back_map():
    select.set(select.get() - 1)
    frame.cell_selection()["rows"] = select


@reactive.effect
@reactive.event(input.save, ignore_none=False)
def x():
    data.loc[select.get(), "Verificada"] = 'S' if input.resp.get() else 'N'
    data.loc[select.get(), "Respons"] = input.respons.get()
    


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
        print("Got FIle", input.file1()[0])
        data.set(pandas.read_csv(input.file1()[0]["datapath"]))
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
        with ui.card():

            @render.ui
            def progress():
                return ui.input_slider(
                    "slider", "", 0, dat()["Nome"].size, select.get(), width="100%"
                )

            with ui.layout_columns():
                ui.input_action_button("back", "Anterior", class_="btn-sm")
                ui.input_action_button("go", "Proxima", class_="btn-sm")

        with ui.layout_columns():
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

            with ui.navset_card_pill(id="tab"):
                with ui.nav_panel("Visualizar"):

                    @render.ui
                    def nb():
                        return [
                            ui.markdown(f"""## {currentRow()[0]}"""),
                            ui.markdown(
                                f"""### INEP:[{currentRow()['CO_ENTIDADE']}](https://qedu.org.br/api/search/?text={currentRow()['CO_ENTIDADE']})"""
                            ),
                            ui.markdown(f"""{currentRow()['NO_ENTIDADE']}"""),
                        ]

                    @render.ui
                    def addrs():
                        return ui.markdown(f"""{currentRow()['End']}""")

                    @render.ui
                    def sv():
                        return ui.markdown(f"""[GoogleMaps]({currentRow()['Link']})""")

                with ui.nav_panel("Editar"):

                    @render.ui
                    def info():
                        return [
                            ui.input_text(
                                "name",
                                "Nome da Escola",
                                value=f"""{currentRow()['Nome']}""",
                            ),
                            ui.input_select(
                                "city",
                                "Municipio",
                                {
                                    "nan": "Não Informado",
                                    "Capão da Canoa": "Capão da Canoa",
                                    "Caraá": "Caraá",
                                    "Cidreira": "Cidreira",
                                    "Imbé": "Imbé",
                                    "Itati": "Itati",
                                    "Maquiné": "Maquiné",
                                    "Mostardas": "Mostardas",
                                    "Osório": "Osório",
                                    "Palmares do Sul": "Palmares do Sul",
                                    "Rolante": "Rolante",
                                    "Santo Antônio da Patrulha": "Santo Antônio da Patrulha",
                                    "Tavares": "Tavares",
                                    "Terra de Areia": "Terra de Areia",
                                    "Torres": "Torres",
                                    "Tramandaí": "Tramandaí",
                                    "Três Cachoeiras": "Três Cachoeiras",
                                    "Xangri-lá": "Xangri-lá",
                                },
                                selected=currentRow()["NO_MUNICIPIO"],
                            ),
                            ui.input_select(
                                "zona",
                                "Zona",
                                {
                                    "r": "Rural",
                                    "u": "Urbana",
                                },
                                selected=(
                                    "u" if currentRow()["TP_LOCALIZACAO"] == 1 else "r"
                                ),
                            ),
                            ui.input_select(
                                "rede",
                                "Rede",
                                {
                                    "pu": "Publica",
                                    "pi": "Privada",
                                },
                                selected=(
                                    "pi"
                                    if currentRow()["TP_DEPENDENCIA"] == 4
                                    else "pu"
                                ),
                            ),
                            ui.input_numeric(
                                "students",
                                "Numero de Estudantes",
                                value=currentRow()["Alunos"],
                                min=1,
                            ),
                            ui.input_select(
                                "etp",
                                "Etapa",
                                {
                                    "Infantil": "Infantil",
                                    "Fundamental": "Fundamental",
                                    "Medio": "Medio",
                                },
                            ),
                            ui.input_checkbox_group(
                                "schl_data",
                                "Dados extra",
                                {
                                    "eja": "Eja",
                                    "idg": "Indigena",
                                    "qdr": "Quadra",
                                    "bib": "Biblioteca",
                                    "pto": "Patio",
                                    "int": "Internet",
                                },
                            ),
                            ui.input_text(
                                "lat",
                                "Latitude, Longitude",
                                value=f"{currentRow()["Lat"]}, {currentRow()["Long"]}",
                            ),
                        ]

                with ui.nav_panel("Checagem"):

                    @render.ui
                    def ctrl():
                        return [
                            ui.input_switch(
                                "resp",
                                "Verificado",
                                value=currentRow()["Verificada"] == "S",
                            ),
                            ui.input_text(
                                "respons", "Responsavel", value=currentRow()["Respons"]
                            ),
                            ui.input_action_button(
                                "save", "Salvar", class_="btn-primary"
                            ),
                        ]

        with ui.layout_columns():

            @render.download(label="Download CSV")
            def download1():
                """
                This is the simplest case. The implementation simply returns the name of a file.
                Note that the function name (`download1`) determines which download_button()
                corresponds to this function.
                """
                path = Path(__file__).parent / input.file1()[0]["name"]
                data.get().to_csv(path, index=False)
                return str(path)


# Reactions
def save():
    d = data.get()
    d.loc[select.get(), "Verificada"] = "S" if input.resp.get() else "N"
    d.loc[select.get(), "Respons"] = input.respons.get()
    
    lat, long = input.lat.get().split(", ")
    d.loc[select.get(), "Lat"] = lat
    d.loc[select.get(), "Long"] = long

    d.loc[select.get(), "Nome"] = input.name.get()
    d.loc[select.get(), "Municipio"] = input.city.get()
    d.loc[select.get(), "Zona"] = "Rural" if input.zona.get() == "r" else "Urbana"
    d.loc[select.get(), "Rede"] = "Publica" if input.rede.get() == "pu" else "Privada"

    d.loc[select.get(), "Alunos"] = input.students.get()
    d.loc[select.get(), "Etapa"] = input.etp.get()

    slt = input.schl_data.get()
    d.loc[select.get(), "EJA"] = "Sim" if "eja" in slt else "Não"
    d.loc[select.get(), "Indigena"] = "Sim" if "idg" in slt else "Não"
    d.loc[select.get(), "Quadra"] = "Sim" if "qdr" in slt else "Não"
    d.loc[select.get(), "Biblioteca"] = "Sim" if "bib" in slt else "Não"
    d.loc[select.get(), "Patio"] = "Sim" if "pto" in slt else "Não"
    d.loc[select.get(), "Internet"] = "Sim" if "int" in slt else "Não"

    data.set(d)


@reactive.effect
@reactive.event(input.save, ignore_none=False)
def x():
    print("Pressed")
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

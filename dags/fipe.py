# -*- coding: utf-8 -*-
import scrapy
import json
import os


class FipeSpider(scrapy.Spider):
    name = 'Fipe'
    start_urls = ['https://veiculos.fipe.org.br']
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    MESES = {"1": 'janeiro', "2": 'fevereiro', "3": 'março',
             "4": 'abril', "5": 'maio', "6": 'junho',
             "7": 'julho', "8": 'agosto', "9": 'setembro',
             "10": 'outubro', "11": 'novembro', "12": 'dezembro'}

    def __init__(self, ano: int, mes: int, **kwargs):
        super(FipeSpider, self).__init__(**kwargs)
        self.ano = str(ano)
        self.mes = str(mes)
        self.referencia = f"{self.MESES[self.mes]}/{self.ano} "

    def parse(self, response):
        yield scrapy.Request(url="https://veiculos.fipe.org.br/api/veiculos//ConsultarTabelaDeReferencia",
                             callback=self.parse_tabela_referencia, headers=FipeSpider.headers, method="POST")

    def parse_tabela_referencia(self, response):
        tabela_referencias = json.loads(response.text)
        tabela_referencias = {referencia["Mes"]:referencia["Codigo"] for referencia in tabela_referencias}
        codigo = tabela_referencias[self.referencia]
        formdata = {"codigoTabelaReferencia": codigo,
                        "codigoTipoVeiculo": "1"}

        yield scrapy.Request(url="https://veiculos.fipe.org.br/api/veiculos/ConsultarMarcas",
                                 callback=self.parse_marca, headers=FipeSpider.headers,
                                 method="POST", body=json.dumps(formdata),
                                 meta={"formdata":formdata.copy()})

    def parse_marca(self, response):
        tabela_marcas = json.loads(response.text)
        formdata = response.meta["formdata"]
        for marca in tabela_marcas[:2]:
            formdata["codigoMarca"] = marca["Value"]
            yield scrapy.Request(url="https://veiculos.fipe.org.br/api/veiculos//ConsultarModelos",
                                 callback=self.parse_modelo, headers=FipeSpider.headers,
                                 method="POST", body=json.dumps(formdata),
                                 meta={"formdata": formdata.copy()})

    def parse_modelo(self, response):
        tabela_modelos = json.loads(response.text)
        formdata = response.meta["formdata"]
        for modelo in tabela_modelos["Modelos"][:10]:
            formdata["codigoModelo"] = modelo["Value"]
            yield scrapy.Request(url="https://veiculos.fipe.org.br/api/veiculos//ConsultarAnoModelo",
                                 callback=self.parse_ano, headers=FipeSpider.headers,
                                 method="POST", body=json.dumps(formdata), meta={"formdata": formdata.copy()})

    def parse_ano(self, response):
        tabela_anos = json.loads(response.text)
        formdata = response.meta["formdata"]
        for ano in tabela_anos:
            formdata["anoModelo"], formdata["codigoTipoCombustivel"] = ano["Value"].split("-")
            formdata["tipoVeiculo"] = "carro"
            formdata["tipoConsulta"] = "tradicional"
            yield scrapy.Request(url="https://veiculos.fipe.org.br/api/veiculos//ConsultarValorComTodosParametros",
                                 callback=self.parse_pesquisa, headers=FipeSpider.headers,
                                 method="POST", body=json.dumps(formdata.copy()), meta={"formdata": formdata})

    def parse_pesquisa(self, response):
        pesquisa = json.loads(response.text)
        yield pesquisa
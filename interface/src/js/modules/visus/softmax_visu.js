export function histogram(val) {
    var vlSpec = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        data: { values: val },
        config : {
            background : "transparent",
            view: {stroke: null},
            axis: {grid: false},
            facet: {spacing: 0},
        },
        facet : {
            field: "dimension", type: "nominal", sort: ['groupBy', 'aggregation', 'min', 'avg', 'max', 'sum'],
            header: {orient: "bottom", labelColor: '#fff', labelFontSize: 15, labelPadding: 15, title: null}
        },
        spec : {
            width: 50, height: 100,
            encoding : {
                x: {
                    field: "add_remove",
                    axis: {
                            labelColor: '#fff', labelFontSize: 15, labelAngle: 0, labelPadding: -30,
                            domainWidth : 0, ticks : false, title: null
                        }
                },
                y: {
                    field: "score", type: 'quantitative',
                    axis: null
                },
            },
            layer : [
                {
                    mark : {
                        type: "bar", stroke: "rgb(71, 71, 71)",
                        color : {expr: "if(datum.add_remove == '+', '#26a566', '#a5264a') "}
                    }
                },
                {
                    mark : {type: "text", dy: -10, color: "white"},
                    encoding : {
                        text: {field: "score", type: "quantitative", format: ".0%"}
                    }
                }
            ]  
        }
    }
    return vlSpec
}

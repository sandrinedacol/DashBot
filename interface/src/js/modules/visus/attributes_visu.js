function vegaLite_vlSpec(val) {
    var vlSpec = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        height: 300,
        width: 300,
        autosize: {
            type: "fit",
            contains: "padding",
            resize: true
        },
        data: { values: val },
        background : "transparent",
        view: {stroke: null}
    }
    return vlSpec
}


export function histogram(val, start) {
    var label_font_size = {true: 25, false: 14}
    var label_color = {true: "#fff", false: "#000"}
    var stroke = {false: "#fff", true: null}
    var color = {false: "#86bcdc", true: "#3887c0"}

    var vlSpec = vegaLite_vlSpec(val)
    
    vlSpec.mark = {
        type : 'bar', stroke: stroke[start],
        cornerRadiusEnd : 4,
    }
    vlSpec.encoding = {
        y : {
            field: "value",
            title: null,
            sort: {field: "value",  order:"descending"},
            axis: {
                labelColor : label_color[start],
                labelExpr: "if(!(isValid(datum.value[1])), datum.value, if(datum.value[0] == datum.value[1], datum.value[0], datum.value[0] + '-' + datum.value[1])) ",
                labelFontSize: label_font_size[start],
                labelPadding: -20, labelAlign: 'left', zindex: 1, labelBound: true,
                ticks: false, grid: false, aria: false
                }
        },
        x : {
            field: "count", type: 'quantitative',
            title: null,
            axis: {
                labelColor : label_color[start],
                labelFontSize: label_font_size[start],
                grid: false, tickMinStep: 1, format: 'd'
            }
        },
        fill : {
            // expr: "datum.perso ? 'rgb(158, 24, 24)' : '" + color[start] + "'"
            // expr: "if(datum.perso, 'rgb(158, 24, 24)', '" + color[start] + "')"
            condition : {
                test : "datum.perso",
                value : "rgb(158, 24, 24)"
            },
            value : color[start]
        }
    }
    return vlSpec
}

export function pie(val, start) {
    var text_color = {false: 'rgb(0,0,0)', true: 'rgb(255,255,255)'}
    var font_size = {false: 16, true: 25}
    var extent = {true: [0.7, 1], false: [0.3, 0.6]}
    var stroke = {true: 'rgb(130,130,130)', false: 'rgb(255,255,255)'}
    
    var vlSpec = vegaLite_vlSpec(val) 
        
    vlSpec.encoding = {
        theta: {field: "count", type: "quantitative", stack: true},
        color: {
            legend: null,
            condition : {
                test: "datum['perso']",
                value :  "rgb(158, 24, 24)"
            },
            field: "value",
            type: "nominal",
            scale: { scheme: {name: "blues", extent: extent[start]}, }
        },
    }
    vlSpec.layer = [{
        mark: {
            type: "arc", outerRadius: 145,
            stroke: stroke[start], strokeWidth: "2"
        },
        encoding: {
            // radius: {
            //     field: "count", type: quantitative,
            //     scale: {type: "sqrt", zero: true, range: [0, 160]}
            // },
        },
    },{
        mark: {
            type: "text",
            fontSize :font_size[start], radius: 90
        },
        encoding: {
            text: { field: "value", type: "nominal" },
            color: { value: text_color[start],}
        }
    }]
    return vlSpec
}



export function word_cloud(val, start) {
    var color_range = {
        false: ["#145ea6", "#2473b4", "#3887c0"],
        true: ["#bcd7eb", "#a2cbe3", "#86bcdc"]
    }
    var vlSpec = {
        $schema: "https://vega.github.io/schema/vega/v5.json",
        padding: 0,
        data: [{
            name: "table",
            values: val,
            transform: [{
                    type: "formula", as: "angle",
                    expr: "[-20, 0, 20][~~(random() * 3)]"
            }]
        }],
        scales: [{
            name: "color",
            type: "ordinal",
            domain: {data: "table", field: "value"},
            range: color_range[start]
        }],
        marks: [{
            type: "text",
            from: {data: "table"},
            encode: {
                enter: {
                    text: {field: "value"},
                    align: {value: "center"},
                    baseline: {value: "alphabetic"},
                    fill: [{
                        test: "datum['perso']",
                        value:'rgb(250, 89, 89)'
                    },{
                        scale: "color",
                        field: "value"
                    }]
                },
            },
            transform: [{
                size: [300,300],
                type: "wordcloud",
                spiral: "rectangular",
                text: {field: "value"},
                rotate: {field: "datum.angle"},
                font: "Helvetica Neue, Arial",
                fontSize: {field: "datum.count"},
                fontSizeRange:[10,35],
                lineBreak : ' ',
                padding: 15
            }]
        }]
    }
    return vlSpec
}
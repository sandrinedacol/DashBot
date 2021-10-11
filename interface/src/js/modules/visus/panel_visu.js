// *********************************************
// SPEC BASE
// *********************************************

function vegaLite_vlSpec(val) {
    var vlSpec = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        height: 600,
        width: 600,
        padding: 20,
        autosize: {
            type: "fit",
            contains: "padding",
            resize: true
        },
        background : 'rgba(255,255,255,0.6)',
        title : {
            offset: 15, fontSize: 22, fontWeight: 600,
            subtitleFontSize: 22, subtitleFontWeight: 600
        },
        data: {values : val},
        layer : [],
        encoding : {},
        view: {stroke: null}
    }
    return vlSpec
}

function vega_vlSpec() {
    var vlSpec = {
        $schema: "https://vega.github.io/schema/vega/v5.json",
        height: 600,
        width: 600,
        padding: 25,
        autosize: {
            contains: "padding",
            resize: true
        },
        background : 'rgba(255,255,255,0.6)',
    }
    return vlSpec
}

// *********************************************
// AXIS
// *********************************************

function get_x_axis(val, attribute) {
    var x_values_length = 0
    val.forEach(row => {
        var label = ""
        if (row[attribute]) {
            if (Array.isArray(row[attribute])) {
                label = row[attribute][0].toString() + '-' + row[attribute][1].toString()
            } else {
                label = row[attribute]
            }
            if (label.length > x_values_length) {
                x_values_length = label.length
            }
        }
    })
    var x_labelAngle = 0
    var labelAlign = 'center'
    if (x_values_length > 5) {
        x_labelAngle = -40
        labelAlign = 'right'
    }
    var x_axis = {
        titleFontSize: 22, titlePadding: 5,
        labelFontSize: 20, labelBound: true,  labelAlign: labelAlign, labelFlush: false, labelAngle: x_labelAngle, // labelPadding: -10,  zindex: 1,
        labelExpr: "if(  isArray(datum.value), if(datum.value[0] == datum.value[1], format(datum.value[0], '.2~s'), format(datum.value[0], '.2~s') + '-' + format(datum.value[1], '.2~s')), if( isNumber(datum.value) ,format(datum.value, '.2~s'), datum.value) ) ",
        grid: false, aria: false, // ticks: false, 
    }
    return x_axis
}

function get_y_axis(val, attribute) {
    var y_labelAngle = 0
    if (attribute) {
        var y_values_length = 0
        val.forEach(row => {
            var label = ""
            if (Array.isArray(row[attribute])) {
                label = row[attribute][0].toString() + '-' + row[attribute][1].toString()
            } else {
                label = row[attribute]
            }
            if (label.length > y_values_length) {
                y_values_length = label.length
            }
        })
        if (y_values_length > 4) {
            y_labelAngle = -40
        }
    }
    var y_axis = {
        titleFontSize: 22, titlePadding: 5,
        labelFontSize: 20, labelBound: true,  labelAlign: 'right', labelFlush: false,  labelAngle: y_labelAngle, labelPadding: 5, // zindex: 1,
        labelExpr: "if(  isArray(datum.value), if(datum.value[0] == datum.value[1], format(datum.value[0], '.2~s'), format(datum.value[0], '.2~s') + '-' + format(datum.value[1], '.2~s')), if( isNumber(datum.value) ,format(datum.value, '.2~s'), datum.value) ) ",
        grid: false, aria: false, tickMinStep: 1, format: 'd', tickCount: 6
    }
    return y_axis
}

// *********************************************
// COLOR
// *********************************************

const discrete_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#17becf']

function yelloworangered(x) {
    var r = Math.max(0, Math.min(255,Math.round(255 - x * 50))) + ''
    var g = Math.max(0, Math.min(255,Math.round(180 - x * 170))) + ''
    var b = Math.max(0, Math.min(255,Math.round(80 - x * 45))) + ''
    return 'rgb(' + r + ', ' + g + ', ' + b + ')'
}
vega.scheme("my_yelloworangered", yelloworangered)

function yellowgreenblue(x) {
    var r = Math.max(0, Math.min(255,Math.round(150 - x * 115))) + ''
    var g = Math.max(0, Math.min(255,Math.round(215 - x * 145))) + ''
    var b = Math.max(0, Math.min(255,Math.round(185 - x * 30))) + ''
    return 'rgb(' + r + ', ' + g + ', ' + b + ')'
}
vega.scheme("my_yellowgreenblue", yellowgreenblue)
  
const color_scale = {
    scale: {
        // scheme: {expr: "['yelloworangered', 'yellowgreenblue', 'lightmulti'][~~(random() * 3)]"},
        scheme: {expr: "['viridis', 'plasma', 'turbo'][~~(random() * 3)]"},
        type: 'linear',
        nice: true,
        domain: {unionWith:[0,1]}
    },
    legend : {
        gradientLength: 450, gradientThickness: 25, offset: 25,
        titleFontSize:20, titleFontWeight: 700, titleAnchor: 'middle', titleBaseline: 'middle', titlePadding: -32,
        direction: "horizontal", orient: 'bottom',
        labelFontSize: 20, labelOffset: 5,
    }
}

function get_count_color_scale(val) {
    var max_count = 0
    val.forEach(row => {
        if (row['*_count'] > max_count) {
            max_count = row['*_count']
        }
    })
    const color_scale ={
        scale: {
            // scheme: {expr: "['yelloworangered', 'yellowgreenblue', 'lightmulti'][~~(random() * 3)]"},
            scheme: 'yellowgreenblue',
            // scheme: {expr: "['my_yelloworangered'][~~(random() * 1)]"},
            extent: [0.3,1],
            type: 'linear',
            nice: true,
            domain: [0,max_count]
        },
        legend : {
            gradientLength: 450, gradientThickness: 25, offset: 25,
            title: "count", titleFontSize:20, titleFontWeight: 700, titleAnchor: 'middle', titleBaseline: 'middle', titlePadding: -32,
            direction: "horizontal", orient: 'bottom',
            labelFontSize: 20, labelOffset: 5,
        },
        field: '*_count',
        type: "quantitative"
    }
    return color_scale
}

// *********************************************
// FIELDS
// *********************************************

function get_aggregate_name(agg_name, panel_aggregates, func) {
    var agg_func = null
    if (panel_aggregates[agg_name][func]) {
        agg_func = agg_name + '_' + func
    }
    return agg_func
}

function get_max_value_of_field(val, field) {
    var max_value = val[0][field]
    val.forEach(row => {
        if (row[field] > max_value) {
                max_value = row[field]
        }
    })
    return max_value
}

// *********************************************************
// HISTOGRAM WITH AGGREGATION ON MULTIPLE ATTRIBUTES
// *********************************************************

function encoding_y(agg_name, func, val, one_or_multiple) {
    var y = {
        field: agg_name + '_' + func, type: "quantitative",
    }
    if (one_or_multiple == 'multiple') {
        y.axis = null
    } else {
        y.axis = get_y_axis(val, null)
        y.title = agg_name
    }
    return y
}

// *********************************************
// HISTOGRAM MIN/MAX/AVG
// *********************************************

function add_one_agg_to_histogram_numeric(vlSpec, aggregation_names, i , val, panel_aggregates, profiles) {
    // FIELD NAMES
    const agg_name = aggregation_names[i]
    const agg_avg = get_aggregate_name(agg_name, panel_aggregates, 'avg')
    const agg_min = get_aggregate_name(agg_name, panel_aggregates, 'min')
    const agg_max = get_aggregate_name(agg_name, panel_aggregates, 'max')
    const agg_sum = get_aggregate_name(agg_name, panel_aggregates, 'sum')
    // Y AXIS
    var y_axis = null
    // axis title
    var y_axis_title = null
    if (aggregation_names.length == 1) {
        y_axis =  get_y_axis(val, null)
        y_axis_title = ""
        if (agg_min && !(agg_avg) && !(agg_max)) {
            y_axis_title = "min(" + agg_name + ")"
        }
        if (agg_avg && !(agg_min) && !(agg_max)) {
            y_axis_title = "avg(" + agg_name + ")"
        }
        if (agg_max && !(agg_min) && !(agg_avg)) {
            y_axis_title = "max(" + agg_name + ")"
        }
        if (y_axis_title == "") {
            y_axis_title = agg_name
        }
    }
    // axis scale
    var max_value = null
    if (agg_max) {
        max_value = get_max_value_of_field(val, agg_max)
    } else if (agg_avg) {
        max_value = get_max_value_of_field(val, agg_avg)
    } else {
        max_value = get_max_value_of_field(val, agg_min)
    }
    var y_scale = {domain: [0, max_value]}
    // text position
    var y_position = ""
    if (agg_max) {
        y_position = agg_max
    } else if (agg_avg) {
        y_position = agg_avg
    } else {
        y_position = agg_min
    }
    var y_offset = 0
    // X AXIS
    const width = 500/val.length/aggregation_names.length
    const x_offset = {expr: width + '* (' + i + '-(' + aggregation_names.length + '-1)/2)'}
    // COUNT : COLOR
    if (panel_aggregates['*']['count']) {
        var encoding_color = get_count_color_scale(val)
    } 
    else {
        var encoding_color = {value: discrete_colors[i]}
    }
    // MULTIPLE AGG OR NOT
    if (aggregation_names.length == 1) {
        var mark_color = 'rgb(0,0,0)'
    } else {
        var mark_color = discrete_colors[i]
    }
    // MIN+MAX : box
    if (agg_min && agg_max) {
        if (agg_avg) {
            vlSpec.layer.push(
                {
                    mark: {type: "tick", opacity: 1, thickness: 10, size: .8*width, xOffset: x_offset},
                    encoding: {
                        y: {field: agg_avg, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                        fill: encoding_color
                    }
                },
            )
        }
        vlSpec.layer.push(
            {
                mark: {type: "bar", opacity: .5, size: .8*width, xOffset: x_offset},
                encoding: {
                    y: {field: agg_min, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    y2: {field: agg_max},
                    fill: encoding_color
                }
            },
        )
    } else if (agg_avg) {
        vlSpec.layer.push(
            {
                mark: {type: "tick", opacity: 1, thickness: 10, size: .8*width, xOffset: x_offset},
                encoding: {
                    y: {field: agg_avg, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    fill: encoding_color
                }
            },
        )
        if (agg_min) {
            vlSpec.layer.push(
                {
                    mark: {type: "bar", opacity: .5, size: .8*width, xOffset: x_offset},
                    encoding: {
                        y: {field: agg_min, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                        y2: {field: agg_avg},
                        fill: encoding_color
                    }
                },
            )
        }
        if (agg_max) {
            vlSpec.layer.push(
                {
                    mark: {type: "bar", opacity: .5, size: .8*width, xOffset: x_offset},
                    encoding: {
                        y: {field: agg_avg, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                        y2: {field: agg_max, type: "quantitative"},
                        fill: encoding_color
                    }
                },
            )
        }
    } else if (agg_min) {
        if (max_value == 0) {
            y_scale = {domain: [0, 1]}
            vlSpec.transform = [{
                calculate: "datum." + agg_min + " + 1", as: agg_min + "_up"
            }]
        } else{
            y_scale = {domain: [0, 1.2 * max_value]}
            vlSpec.transform = [{
                calculate: "datum." + agg_min + " + " + max_value + "/5", as: agg_min + "_up"
            }]
        }
        vlSpec.layer.push(
            {
                mark: {type: "bar", opacity: .5, size: .8*width, stroke: null, xOffset: x_offset},
                encoding: {
                    y: {field: agg_min, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    y2: {field: agg_min + "_up", type: "quantitative"},
                    fill: encoding_color
                }
            },
            {
                mark: {
                    type: "bar", size: .8*width, stroke: null, xOffset: x_offset,
                    color: { 
                        x1: 1, y1: 1,
                        x2: 1, y2: 0,
                        gradient: "linear",
                        stops: [
                            {offset: 0, color: "rgba(255, 255, 255, 0)"},
                            {offset: 1, color: "white"}
                        ]
                    }
                },
                encoding: {
                    y: {field: agg_min, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    y2: {field: agg_min + "_up", type: "quantitative"},
                }
            }
        )
    } else if (agg_max) {
        if (max_value == 0) {
            y_scale = {domain: [0, 1]}
            vlSpec.transform = [{
                calculate: "datum." + agg_max + " - 1", as: agg_max + "_down"
            }]
        } else{
            y_scale = {domain: [0, 1.2 * max_value]}
            vlSpec.transform = [{
                calculate: "datum." + agg_max + " - " + max_value + "/5", as: agg_max + "_down"
            }]
        }
        vlSpec.layer.push(
            {
                mark: {type: "bar", opacity: .5, size: .8*width, stroke: null, xOffset: x_offset},
                encoding: {
                    y: {field: agg_max + "_down", type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    y2: {field: agg_max, type: "quantitative"},
                    fill: encoding_color
                }
            },
            {
                mark: {
                    type: "bar", size: .8*width, stroke: null, xOffset: x_offset,
                    color: { 
                        x1: 1, y1: 0,
                        x2: 1, y2: 1,
                        gradient: "linear",
                        stops: [
                            {offset: 0, color: "rgba(255, 255, 255, 0)"},
                            {offset: 1, color: "white"}
                        ]
                    }
                },
                encoding: {
                    y: {field: agg_max + "_down", type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    y2: {field: agg_max, type: "quantitative"},
                }
            }
        )
    }  
    // SUM : TEXT
    if (agg_sum) {
        vlSpec.layer.push({
            mark: {
                type : 'text', align: 'center', fontSize: 20, text: 'sum:',
                yOffset: -40, xOffset : x_offset,
                color : mark_color
            },
            encoding: {
                y: {field: y_position, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
            }
        })
        vlSpec.layer.push({
            mark: {
                type : 'text', align: 'center', fontSize: 20,
                yOffset: -20, xOffset : x_offset,
                color : mark_color
            },
            encoding: {
                y: {field: y_position, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                text: {field: agg_sum, format: '.2~s', type: "quantitative"},
            }
        })
        y_offset = -40
    }
    // PERSONAL INFO
    profiles.forEach(profile => {
        const new_agg = agg_name + '_' + profile
        var profile_name = ''
        profile_name += profile
        vlSpec.layer.push(
            {
                mark: {
                    type: 'point', size: 5*width, opacity: 1, xOffset: x_offset,
                    // fill: {
                    //     x1: 0.5, x2: 0.5, y1: 0.5, y2: 0.5, r1: 0, r2: 0.5,
                    //     gradient: "radial",
                    //     stops: [
                    //         {offset: 1, color: 'rgba(158, 24, 24,0)'},
                    //         {offset: 0, color: 'rgb(158, 24, 24)'}
                    //     ]
                    // }
                    stroke: 'rgb(158, 24, 24)',
                    fill: 'rgba(158, 24, 24,.7)'
                },
                encoding: {
                    y: {field: new_agg, type: 'quantitative', title: y_axis_title, axis: y_axis, scale: y_scale}
                }
            },
            {
                mark: {
                    type: 'text', opacity: 1,
                    color: 'rgb(158, 24, 24)',
                    dy: -25, xOffset: x_offset,
                    text: profile_name, fontSize : 20
                },
                encoding: {
                    y: {field: new_agg, type: 'quantitative', title: y_axis_title, axis: y_axis, scale: y_scale},
                }
            }
        )
    })
    // AGG NAME / Y SCALE : TEXT
    if (aggregation_names.length > 1) {
        vlSpec.layer.push({
            mark: {
                type : 'text', align: 'left', fontSize: 20,
                text: aggregation_names[i],
                angle: -90,
                yOffset: y_offset - 20,
                xOffset : x_offset,
                color : mark_color
            },
            encoding: {
                y: {field: y_position, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale}
            }
        })
        if (agg_avg) {
            vlSpec.layer.push({
                mark: {
                    type : 'text', align: 'center', fontSize: 20,
                    opacity: 1,
                    yOffset: 20,
                    xOffset : x_offset,
                    color : mark_color
                },
                encoding: {
                    y: {field: agg_avg, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                    text: {field: agg_avg, format: '.2~s',},
                }
            })
        } else {
            if (agg_min) {
                vlSpec.layer.push({
                    mark: {
                        type : 'text', align: 'center', fontSize: 20,
                        opacity: 1,
                        yOffset: 20,
                        xOffset : x_offset,
                        color : mark_color
                    },
                    encoding: {
                        y: {field: agg_min, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                        text: {field: agg_min, format: '.2~s',},
                    }
                })
            }
            if (agg_max) {
                vlSpec.layer.push({
                    mark: {
                        type : 'text', align: 'center', fontSize: 20,
                        opacity: 1,
                        yOffset: 20,
                        xOffset : x_offset,
                        color : mark_color
                    },
                    encoding: {
                        y: {field: agg_max, type: "quantitative", title: y_axis_title, axis: y_axis, scale: y_scale},
                        text: {field: agg_max, format: '.2~s',},
                    }
                })
            }
        }
    }
    return vlSpec
}

export function histogram_numeric(val, groupBy_name, aggregation_names, panel_aggregates, profiles) {
    // SPEC
    var vlSpec = vegaLite_vlSpec(val)
    vlSpec.title.text = "Statistics on '" + aggregation_names[0] + "'"
    vlSpec.title.subtitle = "for each '" + groupBy_name + "'"
    vlSpec.layer = []
    vlSpec.encoding = {
        x: {
            field: groupBy_name, type: "ordinal",
            sort: { field: groupBy_name, order:"ascending" },
            axis: get_x_axis(val, groupBy_name)
        },
    }
    if (aggregation_names.length == 1) {
        vlSpec = add_one_agg_to_histogram_numeric(vlSpec, aggregation_names, 0, val, panel_aggregates, profiles)
    } else {
        _.range(aggregation_names.length).forEach(i => {
            vlSpec = add_one_agg_to_histogram_numeric(vlSpec, aggregation_names, i, val, panel_aggregates, profiles)
            vlSpec.resolve = {scale: {y: "independent"}}
        })
    }
    
    return vlSpec
}

// *********************************************
// HISTOGRAM COUNT
// *********************************************

export function histogram_count(val, groupBy_name) {
    var x_axis = get_x_axis(val, groupBy_name)
    var y_axis =  get_y_axis(val, null)
    var color = get_count_color_scale(val)
    var vlSpec = vegaLite_vlSpec(val)
    vlSpec.title.text = "Value distribution of " +  groupBy_name
    vlSpec.layer = [
        {
            mark: {
                type : 'bar',
                stroke: 'rgb(200,200,200)',
                cornerRadiusEnd : 4,
            },
            encoding: {
                y: {
                    field: "*_count", type: "quantitative",
                    title: "count",
                    axis: y_axis
                },
                color: color,
                opacity: {value: .5},
            }
        }
    ]
    vlSpec.encoding = {
        x: {
            field: groupBy_name, type: "ordinal",
            sort: {field: groupBy_name, order:"ascending"},
            axis: x_axis
        },
    }
    return vlSpec
}

// *********************************************
// HISTOGRAM SUM
// *********************************************

function choose_color(panel_aggregates, val, i) {
    var color = null
    if (panel_aggregates['*']['count']) {
        color = get_count_color_scale(val)
    } else {
        color = {value: discrete_colors[i]}
    }
    return color
}

export function histogram_sum(val, groupBy_name, aggregation_name, panel_aggregates) {
    const aggregate = aggregation_name + '_sum'
    // AXIS
    var x_axis = get_x_axis(val, groupBy_name)
    var y_axis =  get_y_axis(val, null)
    // TITLE
    const title = "Sum of '" + aggregation_name + "'"
    const subtitle = "for each '" + groupBy_name + "' groups"
    // SPEC
    var vlSpec = vegaLite_vlSpec(val)
    vlSpec.title.text = title
    vlSpec.title.subtitle = subtitle
    vlSpec.layer = [
        {
            mark: {
                type : 'bar',
                stroke: 'rgb(200,200,200)',
                cornerRadiusEnd : 4,
            },
            encoding: {
                y: {
                    field: aggregate, type: "quantitative",
                    title: "sum(" + aggregation_name + ")",
                    axis: y_axis
                },
                color: choose_color(panel_aggregates, val, 0),
                opacity: {value: .5},
            }
        }
    ]
    vlSpec.encoding = {
        x: {
            field: groupBy_name, type: "ordinal",
            sort: {field: groupBy_name, order:"ascending"},
            axis: x_axis
        },
    }
    return vlSpec
}

export function histogram_sum_multiple(val, groupBy_name, aggregation_names, panel_aggregates) {
    const width = 500 / aggregation_names.length / val.length
    
    // SPEC
    var vlSpec = vegaLite_vlSpec(val)
    vlSpec.title.text = "Sum of "
    vlSpec.title.subtitle = "for each '" + groupBy_name + "' groups"
    vlSpec.layer = []
    vlSpec.encoding = {
        x: {
            field: groupBy_name, type: "ordinal",
            axis: get_x_axis(val, groupBy_name),
        }
    }

    _.range(aggregation_names.length).forEach(i => {
        // AXIS
        const y = {field: aggregation_names[i] + '_sum', type: "quantitative", axis: null}
        const x_offset = {expr: width + '* (' + i + '-(' + aggregation_names.length + '-1)/2)'}
        // TITLE
        if (i > 0) {
            if (i == aggregation_names.length - 1) {
                vlSpec.title.text += " & "
            } else {
                vlSpec.title.text += ', '
            }
        }
        vlSpec.title.text += "'" + aggregation_names[i] + "'"
        // BARS
        vlSpec.layer.push({
            mark : {
                type : 'bar',
                stroke: 'rgb(200,200,200)',
                cornerRadiusEnd : 4,
                width: width * 0.9,
                strokeWidth: 2,
                xOffset : {expr: width + '* (' + i + '-(' + aggregation_names.length + '-1)/2)'}
            },
            encoding : {
                y: encoding_y(aggregation_names[i], 'sum', val, 'multiple'),
                opacity: {value: 0.5},
                color: choose_color(panel_aggregates, val, i),
            }
        })
        // TEXT
        vlSpec.layer.push({
            mark: {
                type : 'text', align: 'left', fontSize: 20,
                text: aggregation_names[i],
                angle: -90,
                yOffset: -30,
                xOffset : x_offset,
                color : discrete_colors[i]
            },
            encoding: {
                y: y,
            }
        })
        vlSpec.layer.push({
            mark: {
                type : 'text', align: 'center', fontSize: 20,
                yOffset: -10,
                xOffset : x_offset,
                color : discrete_colors[i]
            },
            encoding: {
                y: y,
                text: {field: aggregation_names[i] + '_sum', type: "quantitative", format: ".2~s"},
            }
        })
    })

    vlSpec.resolve = {scale: {y: "independent"}}
    return vlSpec
}

// *********************************************
// RADIAL PLOT
// *********************************************

export function radial_plot_count(val, groupBy_name) {
    // RADIUS SIZE
    var max_value = 0
    val.forEach(entry => {
        if (entry['*_count'] > max_value) {
            max_value = entry['*_count']
        }
    })
    // SPEC
    var vlSpec = vegaLite_vlSpec(val)
    // TITLE
    vlSpec.title.text = "Value distribution of " + groupBy_name
    // ENCODING
    vlSpec.encoding = {
        theta: {field: groupBy_name, type: "nominal", stack: true},
    }
    // LAYERS ARC
    var color = get_count_color_scale(val)
    color.legend.gradientLength = 560
    vlSpec.layer.push({
        mark: {
            type: "arc", stroke: "rgb(170,170,170)",
            innerRadius: 20,
            outerRadius: {expr: "20 + datum['*_count'] * 190 /" + max_value},
        },
        encoding : {
            opacity : {value: .5},
            color: color
        }
    })
    // LAYER TEXT
    vlSpec.layer.push({
        mark: {
            type: "text", fontSize : 22,
            radius: 100,
        },
        encoding: {
            text: {field: groupBy_name, type: "nominal"},
            color: {value: 'black'},
        }
    })
    return vlSpec
}

export function radial_plot_sum(val, groupBy_name, aggregation_name, panel_aggregates) {
    // RADIUS SIZE
    var max_value = 0
    val.forEach(entry => {
        if (entry[aggregation_name + '_sum']> max_value) {
            max_value = entry[aggregation_name + '_sum']
        }
    })
    // SPEC
    var vlSpec = vegaLite_vlSpec(val)
    // TITLE
    vlSpec.title.text = "Sum of '" + aggregation_name + "'"
    vlSpec.title.subtitle = "for each '" + groupBy_name + "' groups"
    // ENCODING
    vlSpec.encoding = {
        theta: {field: groupBy_name, type: "nominal", stack: true},
    }
    // LAYERS ARC
    // radius = sum
    const outer_radius = "datum['" + aggregation_name + "_sum']"
    
    var color = {}
    // IF COUNT : COUNT = COLOR
    if (panel_aggregates['*']['count']) {
        color = get_count_color_scale(val)
    // IF NOT COUNT : NO COLOR
    } else {
        color = {value: _.sample(discrete_colors)}
    }

    vlSpec.layer.push({
        mark: {
            type: "arc", stroke: "rgb(170,170,170)",
            innerRadius: 20,
            outerRadius: {expr: '20 + (' + outer_radius + ') * 190 /' + max_value},
        },
        encoding : {
            opacity : {value: .5},
            color: color
        }
    })


    // LAYER TEXT
    vlSpec.layer.push({
        mark: {
            type: "text", fontSize : 22,
            radius: 100,
        },
        encoding: {
            text: {field: groupBy_name, type: "nominal"},
            color: {value: 'black'},
        }
    })
    return vlSpec
}

// *********************************************
// WORD CLOUD
// *********************************************

export function word_cloud(val, groupBy_name, aggregation_name, panel_aggregates) {
    // color = avg, size = count, angle = min, gras= max
    
    var aggregate = null
    var title = null
    var subtitle = null
    if (aggregation_name == "*") {
        aggregate = '*_count'
        title = "Value distribution of '" + groupBy_name +"'"
    } else {
        if (panel_aggregates[aggregation_name].sum) {
            aggregate = aggregation_name + '_sum'
            title = 'Sum'
        }
        if (panel_aggregates[aggregation_name].min) {
            aggregate = aggregation_name + '_min'
            title = 'Minimum'
        }
        if (panel_aggregates[aggregation_name].max) {
            aggregate = aggregation_name + '_max'
            title = 'Maximum'
        }
        if (panel_aggregates[aggregation_name].avg) {
            aggregate = aggregation_name + '_avg'
            title = 'Average'
        }
        title += ' of ' + aggregation_name
        subtitle = "for each '" + groupBy_name + "' group"
    }
    
    var color_range = _.sample([["#482575", "#21918d", "#35b779"], ["#57106d", "#bb3755", "#fa8d0b"], ["#8f83b7", "#797979", "#e8932f"]])

    var vlSpec = vega_vlSpec()
        
    vlSpec.data = [{
        name: "table",
        values: val,
        transform: [{
                type: "formula", as: "angle",
                expr: "[-45, 0, 45][~~(random() * 3)]"
        }]
    }],
    vlSpec.scales = [{
        name: "color",
        type: "ordinal",
        domain: {data: "table", field: groupBy_name},
        range: color_range
    }]
    vlSpec.layout = {
        padding: 0,
        columns: 1,
        align: "each",
        center: true
    }
    vlSpec.marks = [{
        type: 'group',
        marks: [{
            type: "text",
            encode: {
                enter: {
                    x: {value: 0}, y: {value: 0},
                    text: { value: title},
                    dy: {value: 22}, fontSize: {value: 22}, fontWeight: {value: 600},
                }
            }
        }]
    },{
        type: 'group',
        marks: [{
            type: "text",
            encode: {
                enter: {
                    x: {value: 0}, y: {value: 0},
                    text: { value: subtitle},
                    fontSize: {value: 22}, fontWeight: {value: 600},
                }
            }
        }]
    },{
        type: 'group',
        marks: [{
            type: "text",
            from: {data: "table"},
            encode: {
                enter: {
                    text: {field: groupBy_name},
                    align: {value: "center"},
                    baseline: {value: "alphabetic"},
                    fill: [
                        // {
                        //     test: "datum['perso']",
                        //     value:'rgb(250, 89, 89)'
                        // },
                        {scale: "color", field: groupBy_name}
                    ]    
                },
            },
            transform: [{
                size: [550 , 500],
                type: "wordcloud",
                spiral: "rectangular",
                text: {field: groupBy_name},
                // rotate: {field: "datum.angle"},
                font: "Helvetica Neue, Arial",
                fontSize: {field: "datum['" + aggregate + "']"},
                // fontWeight: {expr: "if(datum.perso, 'bold' , 'normal')"},
                // fontStyle: {expr: "if(datum.perso, 'bold' , 'normal')"},
                fontSizeRange:[15,40],
                lineBreak : ' ',
                padding: 15
            }]
        }]
    }]
    return vlSpec
}

// *********************************************
// 2 GROUP BY
// *********************************************

export function two_groupBy(val, groupBy_attributes, aggregation_name, panel_aggregates) {
    
    // TITLE
    var title = null
    var subtitle = "('" + groupBy_attributes[0] + "', '" + groupBy_attributes[1] + "') groups"
    if (aggregation_name == '*') {
        title = "Value distribution of"
        
    } else {
        if (panel_aggregates[aggregation_name] == ['sum']) {
            title = "Sum of '" + aggregation_name + "'"
        } else {
            title = "Statistics on '" + aggregation_name + "'"
        }
        subtitle = "for each " + subtitle
    } 
    // COLOR : COUNT
    var color = null
    if (panel_aggregates['*']['count']) {
        color = get_count_color_scale(val)
    } else {
        color = {value: _.sample(discrete_colors)}
    }
    // AXIS : GROUP BY attributes
    var x_axis = get_x_axis(val, groupBy_attributes[0])
    var y_axis = get_y_axis(val, groupBy_attributes[1])
    // MARKS : AGGREGATE(S)
    var legend_title = null
    var aggregate = null
    if (aggregation_name == '*') {
        legend_title = "count"
        aggregate = "*_count"
    } else {
        if (panel_aggregates[aggregation_name]['sum']) {
            legend_title = "sum(" + aggregation_name + ")"
            aggregate = aggregation_name + "_sum"
        } else {
            if (panel_aggregates[aggregation_name]['avg']) {
                legend_title = "avg(" + aggregation_name + ")"
                aggregate = aggregation_name + "_avg"
            } else if (panel_aggregates[aggregation_name]['max']) {
                legend_title = "max(" + aggregation_name + ")"
                aggregate = aggregation_name + "_max"
            } else {
                legend_title = "min(" + aggregation_name + ")"
                aggregate = aggregation_name + "_min"
            }
        }
    }
    
    var vlSpec = vegaLite_vlSpec(val)
    vlSpec.title.text = title
    vlSpec.title.subtitle = subtitle
    vlSpec.layer = [
        {
            mark: {
                type: "point",
                shape: 'circle',
                filled: true,
                stroke: 'rgb(0,0,0)',
                strokeWidth : 1
            },
            encoding: {
                opacity: {value: .8}, 
                size: {
                    field: aggregate, type: "quantitative",
                    scale: {
                        rangeMin:10, rangeMax: 8000,
                        type: 'linear',
                        nice: true,
                    },
                    legend : {
                        // clipHeight: 70,
                        offset: 25,
                        title: legend_title,
                        titleFontSize:20, titlePadding: -10, titleFontWeight: 700, titleAnchor: 'middle',// titleLimit: 80,
                        orient: "right", direction: "vertical", titleBaseline: 'middle', 
                        labelFontSize: 20, gradientThickness: 25, labelOffset: -30,
                        symbolFillColor: 'transparent'
                    }, 
                }
            }
        }
    ]
    vlSpec.encoding = {
        x: {
            field: groupBy_attributes[0], type: "ordinal",
            sort: { field: groupBy_attributes[0], order:"ascending" },
            axis: x_axis
        },
        y : {
            field: groupBy_attributes[1], type: "ordinal",
            sort: { field: groupBy_attributes[1], order:"ascending" },
            axis: y_axis
        },
        color: color
    }
    return vlSpec
}
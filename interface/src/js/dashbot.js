import * as att_visu from './modules/visus/attributes_visu.js'
import * as visu from './modules/visus/panel_visu.js'
import * as softmax_visu from './modules/visus/softmax_visu.js'

var app = new Vue({
    el: '#app',
    data: {
        webService: '',
        dataset_names : [null, 'MovieLens', 'MARS', 'MARS (demo)', 'SERAC', 'Data Avalanche', 'NBA', 'Country', 'test'],
        dataset : {
            name : null,
            n_attributes: null,
            n_rows: null
        },
        attributes : {
            names: [],
            numeric : [],
            characteristics : '',
            info : '',
            dataset : {},
            values : {}, // TODO à regarder quelle est la différence
            value_distributions : {}, // TODO
            rankings : {
                groupBy : [],
                aggregation : []
            },
        },
        personal_data : {
            linked_dict : {'#1': {color: 'rgb(158, 24, 24)'}},
            deep_copy : {'#1': {color: 'rgb(158, 24, 24)'}},
            profile : "#1" // temporaire
        },
        diversity : {
            asked : true,
            achieved : false
        },
        panel : {
            number : 1,
            suggestion : 0,
            groupBy : {},
            aggregates : {},
            query : {select: '', groupBy: ''},
            result_table : '',
            values : {},
            visus: [],
            current_visu: "",
            vizu : {},
        },
        dashboard : {
            size : null,
            panels : {},
            final: {},
        },
        explanation : {
            groupBy : {},
            aggregates : {},
            functions : {},
            add : {
                groupBy : [],
                aggregation : []
            },
            selected : {
                groupBy : [],
                aggregation : []
            }
        },
        mab : {
            algo : 'e-greedy',
            softmax_scores : []
        },
        style: {
            start_generation : {
                height : '75vh',
                background : 'background:rgb(215, 215, 215)'
            },
            stop_generation : {
                height : '95vh',
                background : 'background:rgb(255, 255, 255)'
            },
            multiselect : {
                groupBy : {
                    expanded : false
                },
                aggregation : {
                    expanded : false
                },
            }
        },
        vizu: {
            pie_cloud_threshold : null,
            cloud : false
        },

        preprocess_done : false,
        preprocessed_info_shown : false,
        start_generation : false,
        stop_generation : false
    },

    mounted() {
        this.webService = window.location.origin + '/'
        console.log(this.webService)
    },

    methods: {

        reset_add() {
            this.explanation.add = {
                    groupBy : [],
                    aggregation : []
            }
            this.explanation.selected = {
                groupBy : [],
                aggregation : []
            }
            this.attributes.names.forEach(at => {
                const checkbox = document.getElementById(this.define_id('add-groupBy', at))
                if (!(checkbox.disabled)) {
                    checkbox.checked = false
                }
            })
            this.attributes.numeric.forEach(at => {
                const checkbox = document.getElementById(this.define_id('add-aggregation', at))
                if (!(checkbox.disabled)) {
                    checkbox.checked = false
                }
            })
            const checkbox = document.getElementById(this.define_id('add-aggregation', '*'))
            if (!(checkbox.disabled)) {
                checkbox.checked = false
            }
            // document.getElementById('')
        },

        reset() {
            this.dataset.name = null
            this.personal_data.linked_dict = {'#1': {color: 'rgb(158, 24, 24)'}}
            this.personal_data.deep_copy = {'#1': {color: 'rgb(158, 24, 24)'}}
            this.personal_data.profile = '#1'  // temporaire
            this.diversity.asked = true
            this.diversity.achieved = false
            this.panel.number = 1
            this.panel.suggestion = 0
            this.panel.query = {select: '', groupBy: ''}
            this.panel.values = {}
            this.panel.visus = []
            this.panel.vizu = {}
            this.mab.algo = 'e-greedy',
            this.mab.softmax_scores = []
            this.reset_add()
            this.dashboard.size = null
            this.dashboard.panels = {}
            this.pie_cloud_threshold = null
            this.preprocess_done = false
            this.preprocessed_info_shown = false
            this.start_generation = false
            this.stop_generation = false
        },


        // ------------------------------------------
        // VIZUALISATION
        // ------------------------------------------

 
        get_attributes_vizu(attribute) {
            var start = false
            if (this.start_generation) {
                start = true
            }
            var val = this.attributes.value_distributions[attribute]
            var perso_val = this.personal_data.deep_copy[this.personal_data.profile][attribute]
            var vlSpec = {}
            if ( this.attributes.numeric.includes(attribute) ) {
                val.forEach(item => {
                    const jean_michel = parseFloat(perso_val)
                    if (Number.isNaN(jean_michel) && perso_val) {
                        // this.personal_data.[0]][attribute] = "Please enter a numeric value"
                    } else if (jean_michel >= item['value'][0] && jean_michel <= item['value'][1]) {
                        item['perso'] = true
                    } else {
                        item['perso'] = false
                    }
                })
                vlSpec = att_visu.histogram(val, start)
            } else {
                if (this.attributes.info[attribute].adomSize >= this.vizu.pie_cloud_threshold) {
                    val.forEach(item => {
                        if (perso_val == item['value']) {
                            item['perso'] = true
                        } else {
                            item['perso'] = false
                        }
                    })
                    vlSpec = att_visu.word_cloud(val, start)
                } else {
                    val.forEach(item => {
                        if (perso_val == item['value']) {
                            item['perso'] = true
                        } else {
                            item['perso'] = false
                        }
                    })
                    vlSpec = att_visu.pie(val, start)
                }
            }
            vegaEmbed(document.getElementById(attribute), vlSpec, {actions: false})
        },

        get_panel_vizu() {
            var val = this.panel.values
            // Object.keys(this.personal_data.deep_copy).forEach(profile => {
            //     val.forEach(group => {
            //         group[profile] = false
            //     })
            // })
            
            // aggregation attributes
            var aggregation_numeric = []
            var aggregation_sum = []
            for (const attribute in this.panel.aggregates) {
                if (this.panel.aggregates[attribute].sum ) {
                    aggregation_sum.push(attribute)
                }
                const numeric_functions = ['min', 'max', 'avg']
                numeric_functions.forEach(func => {
                    if (this.panel.aggregates[attribute][func]) {
                        if (!(aggregation_numeric.includes(attribute))) {
                            aggregation_numeric.push(attribute)
                        }
                    }
                })
            }
            var aggregation_attributes = aggregation_sum.concat(aggregation_numeric)
            aggregation_attributes = [...new Set(aggregation_attributes)]
            var aggregation_attribute = null
            if (aggregation_attributes.length == 0) {
                aggregation_attribute = '*'
            } else if (aggregation_attributes.length == 1) {
                aggregation_attribute = aggregation_attributes[0]
            } else {                                // Just in case
                aggregation_attribute = _.sample(aggregation_attributes)
            }
            // GROUP BY attributes
            var groupBy_attributes = []
            for (const key in this.panel.groupBy) {
                if (this.panel.groupBy[key]) {
                    groupBy_attributes.push(key)
                }
            }
            var groupBy_attribute = null
            if (groupBy_attributes.length == 1) {
                groupBy_attribute = groupBy_attributes[0]
            } else {                                 // Just in case
                groupBy_attribute = _.sample(groupBy_attributes)
            }
            // personal info
            var personal_info = {}
                // groupby
            Object.keys(this.personal_data.deep_copy).forEach(profile => {
                var values = {}
                const filled_groupBy_attributes = this.find_filled_gb_att(groupBy_attributes, profile)
                val.forEach(group => {
                    filled_groupBy_attributes.forEach(att => {
                        const perso_val = this.personal_data.deep_copy[profile][att]
                        if (this.is_perso_val_in_group(group, att, perso_val)) {
                            values[att] = group[att]
                        }
                    })
                personal_info[profile] = values
                })
            })
                // agg
            Object.keys(this.personal_data.deep_copy).forEach(profile => {
                const filled_agg_attributes = this.find_filled_gb_att(aggregation_numeric, profile)
                filled_agg_attributes.forEach(agg_att => {
                    var perso_val = this.personal_data.deep_copy[profile][agg_att]
                    if (!(Number.isNaN(parseFloat(perso_val)))) {
                        perso_val = parseFloat(perso_val)
                    }
                    val.forEach(group => {
                        if (personal_info[profile][groupBy_attributes[0]] == group[groupBy_attributes[0]]) {
                            const new_agg_name = agg_att + '_' + profile
                            group[new_agg_name] = perso_val
                        }
                    })
                    
                })
            })
                // profiles
            var profiles = Object.keys(this.personal_data.deep_copy)

            // spec
            var vlSpec = {}
            if (this.panel.current_visu == "histogram_numeric") {
                vlSpec = visu.histogram_numeric(val, groupBy_attribute, aggregation_numeric, this.panel.aggregates, profiles)
            } else if (this.panel.current_visu == "histogram_count") {
                vlSpec = visu.histogram_count(val, groupBy_attribute)
            } else if (this.panel.current_visu == "histogram_sum") {
                vlSpec = visu.histogram_sum(val, groupBy_attribute, aggregation_sum[0], this.panel.aggregates)
            } else if (this.panel.current_visu == "histogram_multiple_sum") {
                vlSpec = visu.histogram_sum_multiple(val, groupBy_attribute, aggregation_sum, this.panel.aggregates)
            } else if (this.panel.current_visu == "radial_plot_count") {
                vlSpec = visu.radial_plot_count(val, groupBy_attribute)
            } else if (this.panel.current_visu == "radial_plot_sum") {
                vlSpec = visu.radial_plot_sum(val, groupBy_attribute, aggregation_sum[0], this.panel.aggregates)
            } else if (this.panel.current_visu == "word_cloud") {
                vlSpec = visu.word_cloud(val, groupBy_attribute, aggregation_attribute, this.panel.aggregates)
            } else if (this.panel.current_visu == "two_groupBy") {
                vlSpec = visu.two_groupBy(val, groupBy_attributes, aggregation_attribute, this.panel.aggregates)
            } else {
                vlSpec = 'no visu available'
            }
            vegaEmbed(document.getElementById(this.define_id('panel', this.panel.number)), vlSpec, {actions: false})
        },

        find_filled_gb_att(groupBy_attributes, profile) {
            var filled_groupBy_attributes = []
            groupBy_attributes.forEach(att => {
                if (!(this.personal_data.deep_copy[profile][att] == "")) {
                    filled_groupBy_attributes.push(att)
                }
            })
            return filled_groupBy_attributes
        },

        is_perso_val_in_group(group, attribute, perso_val) {
            var bool = false
            if (Array.isArray(group[attribute])) {
                // discretized attribute
                const jean_michel = parseFloat(perso_val)
                if (jean_michel >= group[attribute][0] && jean_michel <= group[attribute][1]) {
                    bool = true
                }
            } else {
                // not discretized attribute
                if (perso_val == group[attribute]) {
                    bool = true
                }
            }
            return bool
        },

        find_filled_agg_att(numeric_attributes, profile) {
            var filled_aggregation_attributes = []
            aggregation_attributes.forEach(att => {
                if (!(this.personal_data.deep_copy[profile][att] == "")) {
                    filled_aggregation_attributes.push(att)
                }
            })
            return filled_aggregation_attributes
        },

        get_visu_name(string) {
            var name = ""
            if (string.includes('histogram')) {
                name = "Box Plot"
            } else if (string.includes('radial_plot')) {
                name = "Radial Plot"
            } else if (string.includes('word')) {
                name = "Word Cloud"
            } else if (string.includes('two_groupBy')) {
                name = "Bubble Plot"
            }
            return name
        },

        change_visu_type(visu) {
            this.panel.current_visu = visu
            this.get_panel_vizu()
        },

        get_softmax_scores() {
            var vlSpec = {}
            vlSpec = softmax_visu.histogram(this.mab.softmax_scores)
            vegaEmbed(document.getElementById("softmax_scores"), vlSpec, {actions: false})
        },

        // ------------------------------------------
        // PREPROCESSING
        // ------------------------------------------

        preprocess_data() {
            this.dataset.name = document.getElementById("select_dataset").value
            var url = new URL(this.webService + 'preprocess_data/' + this.dataset.name)
            axios.get(url).then(response => {
                this.dataset.n_attributes = response.data.dataset.n_attributes
                this.dataset.n_rows = response.data.dataset.n_rows
                this.attributes.characteristics = response.data.attributes.characteristics
                this.attributes.value_distributions = response.data.attributes.value_distributions
                this.attributes.names = response.data.attributes.names
                this.attributes.info = response.data.attributes.info
                this.attributes.numeric = response.data.attributes.numeric
                this.attributes.rankings.groupBy = response.data.attributes.rankings.groupBy
                this.attributes.rankings.aggregation = response.data.attributes.rankings.aggregation
                this.vizu.pie_cloud_threshold = response.data.vizu.pie_cloud_threshold
                return this.attributes.rankings.groupBy
            }).then(attributes_names => {
                attributes_names.forEach( attribute => {
                    this.personal_data.linked_dict[this.personal_data.profile][attribute] = ''
                    this.attributes.values[attribute] = []
                    this.attributes.value_distributions[attribute].forEach( entry => {
                        this.attributes.values[attribute].push(entry.value)
                    })
                })
                this.preprocess_done = true
                
                
                const ok = 'true'
                return ok
            }). then(ok => {
                this.show_preprocessed_info()
            })
        },

        show_preprocessed_info() {
            this.personal_data.deep_copy = _.cloneDeep(this.personal_data.linked_dict)
            this.attributes.names.forEach( attribute => {
                this.get_attributes_vizu(attribute)
            })
            this.preprocessed_info_shown = true
        },

        hide_preprocessed_info() {
            this.personal_data.linked_dict = _.cloneDeep(this.personal_data.deep_copy )
            this.preprocessed_info_shown = false
        },

        
        // ---------------------------------------------
        // SET DASHBOARD PARAMETERS
        // ---------------------------------------------

        set_diversity(event) {
            var url = new URL(this.webService + 'set_diversity_to_' + event.target.checked + '_with_start_' + this.start_generation)
            axios.get(url).then(response => {
                this.diversity = response.data.diversity
                this.attributes.rankings = response.data.attributes.rankings
            })
        },

        get_empty_panel_on_dashboard() {
            var empty = 0
            for (const panel_number in this.dashboard.panels) {
                if (this.dashboard.panels[panel_number] == '') {
                    empty += 1
                }
            }
            if (empty == 0) {
                this.dashboard.panels[this.panel.number + 1] = ""
            }
            // this.dashboard.panels.sort( (a,b) => {return a-b})
        },
        
        set_dashboard_size() {
            var dashboard_size = document.getElementById("dashboard_size_range").value
            this.dashboard.size = parseInt(dashboard_size, 10)
            _.range(1, this.dashboard.size + 1).forEach( i => {
                if ( !(Object.keys(this.dashboard.panels).includes(i.toString())) ) {
                    const new_p =  JSON.stringify(i)
                    this.dashboard.panels[new_p] = ""
                }
            })
            Object.keys(this.dashboard.panels).forEach( panel_id => {
                if (parseInt(panel_id, 10) > dashboard_size) {
                    delete this.dashboard.panels[panel_id]
                }
            })
            document.getElementById("clear_dashboard_size_button").disabled = false
            var panels = []
                Object.keys(this.dashboard.panels).forEach(panel_id => {
                    if (this.dashboard.panels[panel_id] != "") {
                        panels.push(parseInt(panel_id,10))
                    }
                    
                })
                document.getElementById("dashboard_size_range").min = _.max(panels)
        },  

        clear_dashboard_size() {
            const transfer_area = document.getElementById('transfer')
            Object.keys(this.dashboard.panels).forEach( panel_number => {
                if (this.dashboard.panels[panel_number] != 0) {
                    var panel_copy = document.getElementById(panel_number).lastChild.firstChild
                    transfer_area.appendChild(panel_copy)
                }
            })
            this.dashboard.size = null
            this.dashboard.panels = {}
            _.range(1, this.panel.number).forEach( panel_number => {
                const jean_michel = panel_number.toString()
                this.dashboard.panels[jean_michel] = jean_michel
                const target = document.getElementById(panel_number).lastChild
                target.appendChild(transfer_area.firstChild)
            } )
            this.dashboard.panels[this.panel.number] = ""
            document.getElementById("clear_dashboard_size_button").disabled = true
            document.getElementById("dashboard_size_range").value = 10
        },

        set_panels_size() {
            // if (!this.dashboard.size && this.stop_generation) {
            //     panels_on_dashboard -= 1
            // }
            
            if (this.stop_generation) {
                var n_panels = 0
                Object.values(this.dashboard.panels).forEach(panel_number => {
                    if (!(panel_number == "")) {
                        n_panels += 1
                    }
                })
                if (n_panels > 8) {
                    return 'col-2'
                } else if (n_panels > 2) {
                    return 'col-3'    
                } else {
                    return 'col-4'
                }
            } else {
                const n_panels = Object.keys(this.dashboard.panels).length
                if (n_panels > 4) {
                    return 'col-4'
                } else if (n_panels > 2) {
                    return 'col-5'    
                } else if (n_panels > 1) {
                    return 'col-6'
                } else {
                    return 'col-7'
                }
            }
            
        },

        set_profile_name() {
            var old_name = []
            Object.keys(this.personal_data.linked_dict).forEach(profile => {
                old_name.push(profile)
            })
            old_name = old_name[0]
            this.personal_data.linked_dict[this.personal_data.profile] = this.personal_data.linked_dict[old_name]
            delete this.personal_data.linked_dict[old_name]
            this.personal_data.deep_copy = _.cloneDeep(this.personal_data.linked_dict)
        },
        
        set_personal_data(attribute) {
            this.personal_data.deep_copy[this.personal_data.profile][attribute] = _.cloneDeep(this.personal_data.linked_dict[this.personal_data.profile][attribute])
            this.get_attributes_vizu(attribute)
            var in_current_panel = false
            const agg_func = ['min', 'max', 'avg']
            if (this.panel.groupBy[attribute]) {
                in_current_panel = true
            } else if (agg_func.forEach(func => {this.panel.aggregates[attribute][func]})) {
                in_current_panel = true
            }
            if (in_current_panel) {
                this.get_panel_vizu()
            }
        },



        // ---------------------------------------------
        // STYLE
        // ---------------------------------------------
        
		multiselect_show_hide_checkboxes(event) {
            var checkboxes = event.target.parentElement.nextElementSibling
            if (checkboxes.style.display == "") {
                checkboxes.style.display = "block"
            } else {
                checkboxes.style.display = ""
            }
		},

        multiselect_hide_checkboxes(event) {
            var checkboxes = event.target //.firstChild.lastChild
            checkboxes.style.display = ""
        },

        // ---------------------------------------------
        // GET NEXT PANEL
        // ---------------------------------------------

        get_next_panel_info(response) {
            this.vizu.cloud = false
            this.panel.groupBy = response.data.panel.content.groupBy
            this.reset_add()

            this.explanation.groupBy = _.cloneDeep(this.panel.groupBy)
            Object.keys(this.panel.groupBy).forEach(att => {
                if (this.panel.groupBy[att] == true) {
                    this.explanation.selected.groupBy.push(att)
                }
            })
            this.panel.aggregates = response.data.panel.content.aggregates
            this.explanation.aggregates = _.cloneDeep(this.panel.aggregates)
            Object.keys(this.panel.aggregates).forEach(att => {
                if (!(this.all_false(att, this.panel.aggregates))) {
                    this.explanation.selected.aggregation.push(att)
                }
            })
            this.panel.result_table = response.data.panel.result_table
            this.panel.values = response.data.panel.values_list
            this.attributes.rankings.groupBy = response.data.attributes.rankings.groupBy
            this.attributes.rankings.aggregation = response.data.attributes.rankings.aggregation
            this.diversity = response.data.diversity
            this.panel.query.select = ''
            this.panel.query.groupBy = ''
            Object.keys(this.panel.groupBy).forEach(att => {
                if (this.panel.groupBy[att]) {
                    this.panel.query.groupBy += att + ', '
                    this.panel.query.select += att + ', '
                }
            })
            this.panel.query.groupBy = this.panel.query.groupBy.slice(0,-2)
            this.panel.visus = response.data.panel.visus
            this.panel.current_visu = this.panel.visus[0]
            Object.keys(this.panel.aggregates).forEach(att => {
                Object.keys(this.panel.aggregates[att]).forEach(func => {
                    if (this.panel.aggregates[att][func]) {
                        this.panel.query.select += func + '(' + att + '), '
                    }
                })
            })
            this.panel.query.select = this.panel.query.select.slice(0,-2)
            this.mab.softmax_scores = response.data.softmax_scores
            this.get_softmax_scores()
        },

        start_dashboard_generation() {
            this.personal_data.deep_copy = _.cloneDeep(this.personal_data.linked_dict)
            this.start_generation = true
            Object.assign(this.dashboard.panels, {'1': ''})
            var url = new URL(this.webService + 'start_dashboard_generation')
            axios.get(url).then(response => {
                this.panel.vizu[this.panel.number] = "./jpg/meije_" + this.panel.number + ".jpg"
                this.get_next_panel_info(response)
                return this.attributes.rankings.groupBy
            }).then(groupBy_attributes => {
                groupBy_attributes.forEach( attribute => {
                    this.get_attributes_vizu(attribute)
                })
                this.get_panel_vizu()
            })
        },

        refine_panel() {
            this.panel.suggestion += 1
            // document.getElementById("explanation").attributes["aria-expanded"].nodeValue = "false"
            var url = new URL(this.webService + "process_user_answer")
            url.searchParams.append("user_feedback", false)
            url.searchParams.append("refinement_info", this.mab.algo)
            axios.get(url).then(response => {
                this.get_next_panel_info(response)
                this.panel.vizu[this.panel.number] = "./jpg/meije_" + this.panel.number + ".jpg"
                return this.attributes.rankings.groupBy.slice(0,4)
            }).then(groupBy_attributes => {
                groupBy_attributes.forEach( attribute => {
                    this.get_attributes_vizu(attribute)
                })
                this.get_panel_vizu()
            })
        },

        
        define_id(a, b) {
            return a + '_' + b
        },

        all_false(att, aggregates) {
            const functions = aggregates[att]
            for (const func in functions) {
                const func_bool = functions[func]
                if (func_bool) {
                    return false
                }
            }
            return true
        },

        report_bad_groupBy(att) {
            const checkbox = document.getElementById('remove-groupBy_' + att)
            if (checkbox.checked) {
                this.explanation.groupBy[att] = true
                this.explanation.selected.groupBy.push(att)
            } else {
                this.explanation.groupBy[att] = false
                _.remove(this.explanation.add.groupBy, function(at) { return at == att;})
            }
        },

        report_bad_aggregation(att) {
            const checkbox = document.getElementById('remove-aggregation_' + att)
            if (checkbox.checked) {
                this.explanation.aggregates[att] = _.cloneDeep(this.panel.aggregates[att])
                this.explanation.selected.aggregation.push(att)
            } else {
                for (const func in this.explanation.aggregates[att]) {
                    this.explanation.aggregates[att][func] = false
                    _.remove(this.explanation.add.aggregation, function(at) { return at == att;})
                }
            }
        },

        add_groupBy(att) {
            if (!(this.explanation.add.groupBy.includes(att))) {
                this.explanation.add.groupBy.push(att)
                this.explanation.selected.groupBy.push(att)
                document.getElementById(this.define_id('add-groupBy', att)).checked = true
                var added_groupBy = document.getElementById(this.define_id('added-groupBy', att))
                if (added_groupBy !== null) {
                    added_groupBy.checked = true
                }
                
            } else {
                _.remove(this.explanation.add.groupBy, function(at) { return at == att;})
                _.remove(this.explanation.selected.groupBy, function(at) { return at == att;})
                document.getElementById(this.define_id('add-groupBy', att)).checked = false
                var added_groupBy = document.getElementById(this.define_id('added-groupBy', att))
                added_groupBy.checked = false
            }
        },

        add_aggregation(att) {
            if (!(this.explanation.add.aggregation.includes(att))) {
                this.explanation.add.aggregation.push(att)
                this.explanation.selected.aggregation.push(att)
                document.getElementById(this.define_id('add-aggregation', att)).checked = true
                var added_aggregation = document.getElementById(this.define_id('added-aggregation', att))
                if (added_aggregation !== null) {
                    added_aggregation.checked = true
                }
                
            } else {
                _.remove(this.explanation.add.aggregation, function(at) { return at == att;})
                _.remove(this.explanation.selected.aggregation, function(at) { return at == att;})
                document.getElementById(this.define_id('add-aggregation', att)).checked = false
                var added_aggregation = document.getElementById(this.define_id('added-aggregation', att))
                added_aggregation.checked = false
            }
        },

        change_function(att, func) {
            if (this.vizu.cloud) {
                const checkbox = document.getElementById(this.define_id(func, att))
                if (checkbox.checked) {
                    Object.keys(this.explanation.aggregates[att]).forEach(f => {
                        if (f != func) {
                            this.explanation.aggregates[att][f] = false
                        }
                    })
                }
            }
        },

        reset_explanation() {
            this.explanation.groupBy = _.cloneDeep(this.panel.groupBy)
            this.explanation.aggregates = _.cloneDeep(this.panel.aggregates)
            this.explanation.add.groupBy.forEach(att => {
                var checkbox = document.getElementById(this.define_id('add-groupBy', att))
                checkbox.checked = false
            })
            this.explanation.add.groupBy = []
            this.explanation.add.aggregation.forEach(att => {
                var checkbox = document.getElementById(this.define_id('add-aggregation', att))
                checkbox.checked = false
            })
            this.explanation.add.aggregation = []
            this.explanation.selected.goupBy = []
            Object.keys(this.panel.groupBy).forEach(att => {
                if (this.panel.groupBy[att] == true) {
                    this.explanation.selected.groupBy.push(att)
                }
            })
            this.explanation.selected.aggregation = []
            Object.keys(this.panel.aggregates).forEach(att => {
                if (!(all_false(att, this.panel.aggregates))) {
                    this.explanation.selected.aggregation.push(att)
                }
            })
            for (const att in this.panel.groupBy) {
                if (this.panel.groupBy[att]) {
                    const checkbox = document.getElementById('groupBy_' + att)
                    checkbox.checked = true
                }
                
            }
            for (const att in this.panel.aggregates) {
                if (!(this.all_false(att, this.explanation.aggregates))) {
                    const checkbox = document.getElementById('aggregation_' + att)
                    checkbox.checked = true
                    Object.entries(this.panel.aggregates[att]).forEach(item => {
                        const func = item[0]
                        const func_bool = item[1]
                        const checkbox = document.getElementById(func + '_' + att)
                        if (func_bool) {
                            checkbox.checked = true
                        } else {
                            checkbox.checked = false
                        }
                    })
                }
            }
        },

        apply_explanation() {
            this.panel.suggestion += 1
            // document.getElementById("explanation").attributes["aria-expanded"].nodeValue = "false"
            var url = new URL(this.webService + "process_user_answer")
            
            url.searchParams.append("user_feedback", false)
            // add groupBy
            var groupBy_to_add = ''
            this.explanation.add.groupBy.forEach(att =>{
                groupBy_to_add += '_add_' + att
            })
            //url.searchParams.append("groupBy_to_add", groupBy_to_add)
            // add aggregation
            var aggregation_to_add = ''
            this.explanation.add.aggregation.forEach(att =>{
                aggregation_to_add += '_add_' + att
            })
            //url.searchParams.append("aggregation_to_add", aggregation_to_add)
            
            // remove groupBy
            var groupBy_to_remove = ''
            for (var att in this.panel.groupBy) {
                if (this.panel.groupBy[att] != this.explanation.groupBy[att]) {
                    att = att.replaceAll('/', '-encoded_slash-')
                    groupBy_to_remove += '_remove_' + att
                }
            }
            //url.searchParams.append("groupBy_to_remove", groupBy_to_remove)
            // remove aggregation
            var aggregation_to_remove = ""
            var functions_to_change = ""
            for (var att in this.explanation.aggregates) {
                if (!(this.all_false(att, this.panel.aggregates))) {                // if att is in last panel aggregation
                    att = att.replaceAll('/', '-encoded_slash-')
                    if (this.all_false(att, this.explanation.aggregates)) {         // case 1: while not in explanation
                        aggregation_to_remove += '_remove_' + att                   // --> remove this attribute
                    } else {                                                        // case 2: and still in explanation
                        var f_to_change = '_change_' + att                          // prepare for changing functions
                        const functions = this.explanation.aggregates[att]
                        for (const func in functions) {                             // for each function
                            const func_bool = functions[func]
                            if (func_bool != this.panel.aggregates[att][func]) {    // if there is a difference between explanation and last panel
                                f_to_change += '_with-func-' + func                 // --> change this function
                            }
                        }
                        if (f_to_change != '_change_' + att) {
                            functions_to_change += f_to_change
                        }
                    }
                }
            }
            //url.searchParams.append("aggregation_to_remove", aggregation_to_remove)
            //url.searchParams.append("functions_to_change", functions_to_change)
            const explanations_to_apply = groupBy_to_add + '_AND_' + aggregation_to_add  + '_AND_' + groupBy_to_remove  + '_AND_' + aggregation_to_remove  + '_AND_' + functions_to_change
            url.searchParams.append("refinement_info", explanations_to_apply)
            // response
            axios.get(url).then(response => {
                this.get_next_panel_info(response)
                this.panel.vizu[this.panel.number] = "./jpg/meije_" + this.panel.number + ".jpg"
                return this.attributes.rankings.groupBy.slice(0,4)
            }).then(groupBy_attributes => {
                groupBy_attributes.forEach( attribute => {
                    this.get_attributes_vizu(attribute)
                })
                this.get_panel_vizu()
            })
        },

        // ---------------------------------------------
        // VALIDATE PANEL
        // ---------------------------------------------

        validate_panel() {
            
            if (this.panel.number == this.dashboard.size) {
                this.stop_generation = true
            } else {
                this.panel.number += 1
                this.panel.suggestion = 0
                var panels = []
                Object.keys(this.dashboard.panels).forEach(panel_id => {
                    if (this.dashboard.panels[panel_id] != "") {
                        panels.push(parseInt(panel_id,10))
                    }
                    
                })
                document.getElementById("dashboard_size_range").min = _.max(panels)
                // document.getElementById("explanation").attributes["aria-expanded"].nodeValue = false
                var url = new URL(this.webService + "process_user_answer")
                url.searchParams.append("user_feedback", true)
                url.searchParams.append("refinement_info", null)
                axios.get(url).then(response => {
                    const panel_number = JSON.stringify(this.panel.number)
                    this.get_panel_vizu()
                    this.panel.vizu[this.panel.number] = "./jpg/meije_" + panel_number + ".jpg"
                    this.diversity.achieved = response.data.diversity.achieved
                    this.get_next_panel_info(response)
                    return {
                        'attributes': this.attributes.rankings.groupBy,
                        'diversity_achieved': this.diversity.achieved,
                        'next_panel_value' : this.panel.values
                    }
                }).then(response => {
                    if (response.diversity_achieved) {
                        document.getElementById("diversity_checkbox").disabled = true
                    }
                    response.attributes.forEach( attribute => {
                        this.get_attributes_vizu(attribute)
                    })
                    this.get_panel_vizu()
                })
            }
        },

        allow_drop(event) {
            event.preventDefault();
        },

        drag(event) {
        },
        
        drop(event, i) {
            event.preventDefault()
            const panel_number = JSON.stringify(this.panel.number)
            const panel_id = event.target.parentNode.id
            this.dashboard.panels[panel_id] = panel_number
            const source = document.getElementById( 'panel_in_progress' ).lastChild.firstChild
            this.get_empty_panel_on_dashboard()
            event.target.nextElementSibling.appendChild(source)
            source.draggable = false
            this.validate_panel()
        },

        // ---------------------------------------------
        // END GENERATION
        // ---------------------------------------------

        end_generation() {
            document.getElementById('final').hidden = false
            const dashboard_div_old = document.getElementById('panels_on').firstChild.firstChild
            Object.keys(this.dashboard.panels).forEach(i => {
                if (!(this.dashboard.panels[i] == "")) {
                    const j = parseInt(i, 10) - 1
                    const dashboard_div_new = document.getElementById(this.define_id('final',i)).firstChild
                    const visu_div = dashboard_div_old.children[j].firstChild.lastChild.firstChild
                    // visu_div.classList.add('col-4')
                    dashboard_div_new.appendChild(visu_div)
                }
            })
            this.stop_generation = true

        }



    },

})


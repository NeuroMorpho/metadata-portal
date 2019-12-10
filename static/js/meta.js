function Confirm() {
  var x = confirm("Are you sure?");
  if (x)
      return true;
  else
    return false;
}

function ConfirmDelete() {
  var x = confirm("Are you sure you want to delete?");
  if (x)
      return true;
  else
    return false;
}

function ConfirmArchive() {
  var x = confirm("Are you sure you want to change Archive status of this dataset?");
  if (x)
      return true;
  else
    return false;
}

// enable and disable selections
function enableDisable(bEnable, textBoxID) {
    document.getElementById(textBoxID).disabled = !bEnable
}

// generic select change detection. open new value!
$(document).ready(function(){
    $('select').change(function(){
        var selected_value = $(this).val();
        // var selected_text = $(this).text();
        var selected_name = $(this).attr("name");
        var new_selected_name = "new_" + selected_name;
        var changed_to = $(this).find('option:selected').text();
        // console.log(changed_to);
        if(changed_to == "Not available in the list?"){
            $("input[name=" + new_selected_name + "]").prop('disabled', false);
            $("input[name=" + new_selected_name + "]").show(1000);
            $("input[name=" + new_selected_name + "]").val("");
            // alert('if is executed!');
        } else {
            $("input[name=" + new_selected_name + "]").val("");
            $("input[name=" + new_selected_name + "]").hide(1000);
        }
        if(selected_name == 'lab'){
            // console.log(selected_name);
            // console.log(changed_to);
            if(changed_to == "Not available in the list?"){
                $('#id_new_lab').show(1000);
            } else {
                $('#id_new_lab').hide(1000);
                $("#id_lab_name").val("");
                $("#id_institute").val("");
                $("#id_address").val("");
            }
        }
    });
});

// generic multi select change detection
$(document).ready(function(){
    $('#additional-brain-region, #additional-cell-type').change(function(){
        var selected_value = $(this).is(':checked');;
        var selected_name = $(this).attr("name");
        if(selected_name == "new-region3-input"){
            var new_selected_name = "new_brain_region3";
        } else if(selected_name=="new-cell3-input"){
            var new_selected_name = "new_cell_type3";
        }
        // var changed_to = $(this).find('option:selected').text();
        // console.log(selected_name + " is changed to " + selected_value);
        if(selected_value){
            // $("textarea[name=" + new_selected_name + "]").prop('disabled', false);
            $("textarea[name=" + new_selected_name + "]").show(1000);
        } else if(selected_value==false){
            $("textarea[name=" + new_selected_name + "]").val("");
            $("textarea[name=" + new_selected_name + "]").hide(1000);
        }
    });
});

// select change detection for pixel
$(document).ready(function(){
    $('#id_numerical_units').change(function(){
        var selected_value = $(this).val();
        var selected_name = $(this).attr("name");
        var new_selected_name = "pixel_size";
        // alert(selected_name + " is changed to " + selected_value);
        // console.log(selected_name + " is changed to " + selected_value);
        var changed_to = $(this).find('option:selected').text();
        if(selected_value == "pixel"){
            $("input[name=" + new_selected_name + "]").prop('disabled', false);
            $("input[name=" + new_selected_name + "]").show(1000);
            $("input[name=" + new_selected_name + "]").val("");
            // alert('if is executed!');
        } else {
            // alert('else is executed!');
            $("input[name=" + new_selected_name + "]").val("");
            $("input[name=" + new_selected_name + "]").hide(1000);
            // $("input[name=" + new_selected_name + "]").prop('disabled', true);
            // $("input[name=" + new_selected_name + "]").val(changed_to);
        }
    });
});

// secondary level
$(document).ready(function() {
        $("#id_species, #id_cell_type1, #id_cell_type2, #id_brain_region1, #id_brain_region2").change(function () {
            var url = $("#id_cell_type1").attr("data-url");
            var SelectValue = $(this).val();
            var SelectName = $(this).attr("name");
            var parent1 = "None";
            if(SelectValue == ''){
                // console.log('returning');
                return;
            }
            if(SelectName == 'cell_type1'){
                var next_select = "#id_cell_type2";
            } else if(SelectName == 'cell_type2')  {
                var next_select = "#id_cell_type3";
                var parent1 = document.getElementById("id_cell_type1").value;
                // var parent1 = $("#id_cell_type1").val();
            } else if(SelectName == 'brain_region1')  {
                var next_select = "#id_brain_region2";
                // console.log('logging region1 change');
            } else if(SelectName == 'brain_region2')  {
                var next_select = "#id_brain_region3";
                // var next_select = "keep-order";
                var parent1 = document.getElementById("id_brain_region1").value;
                // var parent1 = $("#id_brain_region1").val();
            } else if(SelectName == 'species')  {
                var next_select = "#id_strain";
            }
            // alert(CellType);
            $.ajax({ // initialize an AJAX request
                url: url, 
                data: {
                    'SelectValue': SelectValue,
                    'SelectName': SelectName,
                    'parent1': parent1,
                },
                success: function (data) {   //
                $(next_select).html(data);  //
                
                // update next level
                switch (next_select) {
                    case "#id_brain_region2":
                        $("#id_brain_region2").trigger("chosen:updated"); break;
                    case "#id_brain_region3":
                        $("#id_brain_region3").trigger("chosen:updated");
                        $('#region3order').val([]); break;
                    case "#id_cell_type2":
                        $("#id_cell_type2").trigger("chosen:updated"); break;
                    case "#id_cell_type3":
                        $("#id_cell_type3").trigger("chosen:updated"); 
                        $('#celltype3order').val([]); break;
                    case "#id_strain":
                        $("#id_strain").trigger("chosen:updated"); break;
                }
            }
        });
    });
});

// integrity
$(document).ready(function() {
        $("#id_dendrites, #id_axon, #id_neurites, #id_processes").change(function () {
            var ChangedtValue = $(this).is(':checked'); 
            var ChangedName = $(this).attr("name");
            // console.log(ChangedName + ', ' + ChangedtValue);
            if(ChangedName == 'axon' && ChangedtValue == true){
                document.getElementById("id_axon_integrity").disabled=false;
                $("#id_neurites, #id_processes").prop('checked', false);
                document.getElementById("id_processes_integrity").disabled=true;
                document.getElementById("id_neurites_integrity").disabled=true;
                document.getElementById("id_processes_integrity").selectedIndex=0;
                document.getElementById("id_neurites_integrity").selectedIndex=0;
            } else if(ChangedName == 'axon' && ChangedtValue == false){
                document.getElementById("id_axon_integrity").disabled=true;
                document.getElementById("id_axon_integrity").selectedIndex=0;
            }
            if(ChangedName == 'dendrites' && ChangedtValue == true){
                document.getElementById("id_dendrites_integrity").disabled=false;
                $("#id_neurites, #id_processes").prop('checked', false)
                document.getElementById("id_processes_integrity").disabled=true;
                document.getElementById("id_neurites_integrity").disabled=true;
                document.getElementById("id_processes_integrity").selectedIndex=0;
                document.getElementById("id_neurites_integrity").selectedIndex=0;
            } else if(ChangedName == 'dendrites' && ChangedtValue == false){
                document.getElementById("id_dendrites_integrity").disabled=true;
                document.getElementById("id_dendrites_integrity").selectedIndex=0;
            }
            if(ChangedName == 'neurites' && ChangedtValue == true){
                document.getElementById("id_neurites_integrity").disabled=false;
                $("#id_dendrites, #id_axon").prop('checked', false);
                document.getElementById("id_dendrites_integrity").disabled=true;
                document.getElementById("id_axon_integrity").disabled=true;
                document.getElementById("id_dendrites_integrity").selectedIndex=0;
                document.getElementById("id_axon_integrity").selectedIndex=0;
            } else if(ChangedName == 'neurites' && ChangedtValue == false){
                document.getElementById("id_neurites_integrity").disabled=true;
                document.getElementById("id_neurites_integrity").selectedIndex=0;
            }
            if(ChangedName == 'processes' && ChangedtValue == true){
                document.getElementById("id_processes_integrity").disabled=false;
                $("#id_dendrites, #id_axon").prop('checked', false);
                document.getElementById("id_dendrites_integrity").disabled=true;
                document.getElementById("id_axon_integrity").disabled=true;
                document.getElementById("id_dendrites_integrity").selectedIndex=0;
                document.getElementById("id_axon_integrity").selectedIndex=0;
            } else if(ChangedName == 'processes' && ChangedtValue == false){
                document.getElementById("id_processes_integrity").disabled=true;
                document.getElementById("id_processes_integrity").selectedIndex=0;
            }
    });
});

// shrinkage
$(document).ready(function() {
        $("#id_tissue_shrinkage, #id_shrinkage_corrected").change(function () {
            var ChangedtValue = $(this).val(); 
            var ChangedName = $(this).attr("name");
            // console.log(ChangedName + ', ' + ChangedtValue);
            if(ChangedName == 'tissue_shrinkage' && ChangedtValue == 'Reported'){
                document.getElementById("id_reported_value").disabled=false;
                document.getElementById("id_reported_xy").disabled=false;
                document.getElementById("id_reported_z").disabled=false;
                document.getElementById("id_shrinkage_corrected").disabled=false;
                // document.getElementById("id_neurites_integrity").selectedIndex=0;
            } 
            else if(ChangedName == 'tissue_shrinkage' && ChangedtValue != 'Reported'){
                document.getElementById("id_reported_value").disabled=true;
                document.getElementById("id_reported_xy").disabled=true;
                document.getElementById("id_reported_z").disabled=true;
                document.getElementById("id_shrinkage_corrected").disabled=true;
                document.getElementById("id_corrected_value").disabled=true;
                document.getElementById("id_corrected_xy").disabled=true;
                document.getElementById("id_corrected_z").disabled=true;

                document.getElementById("id_reported_value").value = '';
                document.getElementById("id_reported_xy").value = '';
                document.getElementById("id_reported_z").value = '';
                document.getElementById("id_shrinkage_corrected").selectedIndex=0;
                document.getElementById("id_corrected_value").value = '';
                document.getElementById("id_corrected_xy").value = '';
                document.getElementById("id_corrected_z").value = '';
            }
            if(ChangedName == 'shrinkage_corrected' && ChangedtValue == 'Y'){
                document.getElementById("id_corrected_value").disabled=false;
                document.getElementById("id_corrected_xy").disabled=false;
                document.getElementById("id_corrected_z").disabled=false;
            } else {
                document.getElementById("id_corrected_value").value = '';
                document.getElementById("id_corrected_xy").value = '';
                document.getElementById("id_corrected_z").value = '';
                document.getElementById("id_corrected_value").disabled=true;
                document.getElementById("id_corrected_xy").disabled=true;
                document.getElementById("id_corrected_z").disabled=true;
            }
    });
});

// working on hovers
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

// data table
$(document).ready(function() {
    // datasets
    $("#datasets").DataTable({
    "pagingType": "full_numbers",
    "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
    "ordering":true,
    "order": [[5, "desc"]],
    "columnDefs":[{
        "targets":6,
        "sortable":false,
        "searchable":false,
    }],
    });
    // search
    $("#search").DataTable({
        language: { search: "Filter the results" },
        "ordering":false,
        "scrollY": '800px',
        "scrollCollapse": true,
        "paging": false
    });
});

// edit button fade in/out
$(document).ready(function(){
    $(parent.window.document).scroll(function() {
        // console.log('scrolling!');
        if ($(this).scrollTop() > 80) {
            $('#down').fadeIn();
        } else {
            $('#down').fadeOut();
        }
    });
});


$(document).ready(function(){
    $(parent.window.document).scroll(function() {
        // console.log('scrolling!');
        var scrollHeight   = $(document).height();
        var scrollPosition = $(window).height() + $(window).scrollTop();
        if ((scrollHeight - scrollPosition) / scrollHeight < 0.035) {
            // when scroll to bottom of the page
            $('#top').fadeOut();
        }
        else {
            $('#top').fadeIn();
        }
    });
});

// chosen
$(document).ready(function() {
    if($('form').is('#metadata-form')){ // check if we are in metadata form or not
        // apply chosen style to the fields
        $('#id_brain_region1').chosen({allow_single_deselect:true}); $('#id_brain_region2').chosen({allow_single_deselect:true}); $('#id_brain_region3').chosen({allow_single_deselect:true});
        $('#id_cell_type1').chosen({allow_single_deselect:true}); $('#id_cell_type2').chosen({allow_single_deselect:true}); $('#id_cell_type3').chosen({allow_single_deselect:true});
        $('#id_species,#id_strain,#id_gender,#id_development_stage').chosen({allow_single_deselect:true});
        $('#id_experimental_condition,#id_experimental_protocol').chosen({allow_single_deselect:true});
        $('#id_stain,id_slice_tickness').chosen({allow_single_deselect:true});
        $('#id_slicing_direction,#id_reconstruction_software').chosen({allow_single_deselect:true});
        $('#id_objective_type').chosen({allow_single_deselect:true});
        $('#id_numerical_units,#id_data_type').chosen({allow_single_deselect:true});
        $('#id_slice_tickness,#id_objective_magnification').chosen({allow_single_deselect:true});
        $('#id_lab').chosen({allow_single_deselect:true});
        var delayTimer;
        // keep track of selection order in brain region
        $('#id_brain_region3').on('change', function(){
            clearTimeout(delayTimer);
            delayTimer = setTimeout(function() {
                var selection = $('#id_brain_region3').getSelectionOrder();
                $('#region3order').val(selection);
                // console.log(selection);
            }, 100); // Will do the ajax stuff after XX ms
       });
        // keep track of selection order in cell type
        $('#id_cell_type3').on('change', function(){
            clearTimeout(delayTimer);
            delayTimer = setTimeout(function() {
                var selection = $('#id_cell_type3').getSelectionOrder();
                $('#celltype3order').val(selection);
                // console.log(selection);
            }, 100); // Will do the ajax stuff after XX ms
       });
    
       // set selection order to the pre saved version
        $(window).bind('load', function() {
            var reg_ord = document.getElementById('region3order').value;
            // console.log('->', $('#id_brain_region3').val() );
            if (reg_ord != '' && reg_ord != 'none' && reg_ord != 'None'){
                $('#id_brain_region3').setSelectionOrder($('#region3order').val().split(','), true);
            } else if ($('#id_brain_region3').val()) {
                // console.log('else');
                $('#region3order').val($('#id_brain_region3').getSelectionOrder());
            }
            var cell_ord = document.getElementById('celltype3order').value;
            if (cell_ord != 'none' && cell_ord != '' && cell_ord != 'None'){
                $('#id_cell_type3').setSelectionOrder($('#celltype3order').val().split(','), true);
            } else if ($('#id_cell_type3').val()) {
                $('#celltype3order').val($('#id_cell_type3').getSelectionOrder());
            }
        });
    }
});

// check new terms in the inserted values
$(document).ready(function(){
    var box_name = $(this).attr("name");
    $('input[name=new_slice_tickness], input[name=new_objective_type], input[name=new_species], input[name=new_strain], input[name=new_gender], input[name=new_development_stage], input[name=new_age_type], input[name=new_brain_region1], input[name=new_brain_region2], input[name=new_cell_type1], input[name=new_cell_type2], input[name=new_experimental_protocol], input[name=new_experimental_condition], input[name=new_stain], input[name=new_slicing_direction], input[name=new_reconstruction_software], input[name=new_objective_type], input[name=new_data_type]').keyup(function(){
    // $('input[name=new_strain], input[name=new_species]').keyup(function(){
        var box_name = $(this).attr("name");
        var select_id = 'id_' + box_name.replace("new_", "");
        // variable which is just typed in the form
        var typed = $('input[name='+box_name+']').val();
        var select_options = $.map($('#'+select_id+' option'), function(e) { return e.text; });
        termSet = FuzzySet(select_options);
        var msg = "";
        var hits = termSet.get(typed,null,0.5);
        // console.log(box_name);
        if(hits !=null ){
            for(var i = 0; i < hits.length; i++) {
                // index 1 is the score! thats why its not been take care of
                msg += "<a href=javascript:quickSelect('$select_id','$v')>"+hits[i][1]+"</a> ";
                msg = msg.replace('$v', select_options.indexOf(hits[i][1]));
                msg = msg.replace('$select_id', select_id);
            }
            $('#'+box_name+'_help').html("Similar hits: " + msg);
            // console.log(box_name);
        } else{
            $('#'+box_name+'_help').html("");
        }
    });
});

// selecting func
function quickSelect(select_id, opt) {
    // var sel = sel;
    var new_box = select_id.replace('id', 'new');
    // var new_box_value = $("input[name=" + new_box + "]").value();
    // var new_box_value = document.getElementsByName(new_box)[0].value;
    var help_id = new_box + "_help";
    var term_list = $.map($('#'+select_id+' option'), function(e) { return e.text; });
    document.getElementById(select_id).selectedIndex = parseInt(opt); 
    $("#"+select_id).trigger('chosen:updated');
    $("#"+help_id).html("");
    $("input[name=" + new_box + "]").val("");
    $("input[name=" + new_box + "]").hide(500);
}

function quickHits() {
    var new_fields = ["new_species", "new_strain", "new_gender", "new_development_stage", "new_age_type", "new_brain_region1", "new_brain_region2", "new_cell_type1", "new_cell_type2", "new_experimental_protocol", "new_experimental_condition", "new_stain", "new_slicing_direction", "new_reconstruction_software", "new_objective_type", "new_data_type"];
    new_fields.forEach(function(field){
        // console.log(field);
        var typed = $('input[name='+field+']').val();;
        var select_id = field.replace('new_', 'id_');
        var update_id = field + "_help";
        if (typed && typed.toLowerCase() !='none'){
            var term_list = $.map($('#'+select_id+' option'), function(e) { return e.text; });
            termSet = FuzzySet(term_list);
            var msg = "";
            var hits = termSet.get(typed,null,0.5);
            if(hits !=null ){
                for(var i = 0; i < hits.length; i++) {
                    msg += "<a href=javascript:quickSelect('$select_id','$v');>"+hits[i][1]+"</a> ";
                    msg = msg.replace('$v', term_list.indexOf(hits[i][1]));
                    // msg = msg.replace('$v', "this is\ a\ test");
                    msg = msg.replace('$select_id', select_id);
                    // console.log(msg);
                }
                // $("#"+update_id).html("Similar hits: " + msg);
                document.getElementById(update_id).innerHTML = "Similar hits: " + msg;
            }
        }
    });
} // end of quickHits()

// show more show less function
$(document).ready(function() {
    // Configure/customize these variables.
    var showChar = 250;  // How many characters are shown by default
    var ellipsestext = "...";
    var moretext = "Show more >";
    var lesstext = "Show less";
    

    $('.more').each(function() {
        var content = $(this).html();
 
        if(content.length > showChar) {
            var c = content.substr(0, showChar);
            var h = content.substr(showChar, content.length - showChar);
            var html = c + '<span class="moreellipses">' + ellipsestext+ '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';
            $(this).html(html);
        }
    });
 
    $(".morelink").click(function(){
        if($(this).hasClass("less")) {
            $(this).removeClass("less");
            $(this).html(moretext);
        } else {
            $(this).addClass("less");
            $(this).html(lesstext);
        }
        $(this).parent().prev().toggle();
        $(this).prev().toggle();
        return false;
    });
});

// if the propagatation is to modify more than 5 groups ask for confirmation.
function prop() {
    var dataset_id = $("#metadata-form").attr("action").match(/\d+/)[0];
    var group_count = 0;
    // console.log(dataset_id);
    $.ajax({
        async : false,
        url: '/ajax/count_groups/',
        data: {'dataset_id': dataset_id},
        dataType: 'json',
        success: function (data) {
            group_count = data.group_count
            // console.log(x);  
        }
    });
    if (group_count >= 5){
        confrimation = confirm(`Propagation will modify ${group_count} groups! Are you sure?`);
        if (confrimation)
            return true;
        else
            return false;
    } else {
        return true;
    }
}

// highlight text in the new terms table
function filterTable(Stxt, table) {
    dehighlight(document.getElementById(table));
    if (Stxt.value.length > 0)
    //   highlight(Stxt.value.toLowerCase(), document.getElementById(table));
      highlight(Stxt.value, document.getElementById(table));
 }

 function dehighlight(container) {
    for (var i = 0; i < container.childNodes.length; i++) {
        var node = container.childNodes[i];
        if (node.attributes && node.attributes['class']
                            && node.attributes['class'].value == 'highlighted') {
                                node.parentNode.parentNode.replaceChild(
                                    document.createTextNode(
                                    node.parentNode.innerHTML.replace(/<[^>]+>/g, "")),
                                    node.parentNode);
                                // Stop here and process next parent
                                return;
        } else if (node.nodeType != 3) {
            // Keep going onto other elements
            dehighlight(node);
        }
    }
}

function highlight(Stxt, container) {
    for (var i = 0; i < container.childNodes.length; i++) {
        var node = container.childNodes[i];
        if (node.nodeType == 3) {
            // Text node
            var data = node.data;
            // check if needs to be case sensitive
            if ($('#case_sensitive_id').is(":checked")){
                // console.log('to be sensitive');
                var data_low = data;
                var Stxt = Stxt;
            } else {
                // console.log('not to be sensitive');
                var data_low = data.toLowerCase();
                var Stxt = Stxt.toLowerCase();
            }
            if (data_low.indexOf(Stxt) >= 0) {
                // console.log(data_low);
                //Stxt found!
                var new_node = document.createElement('span');
                node.parentNode.replaceChild(new_node, node);
                var result;

                // new_node.appendChild(create_node(document.createTextNode(data)));

                while ((result = data_low.indexOf(Stxt)) != -1) {
                    // new_node.appendChild(document.createTextNode(
                    //                         data.substr(0, result)));
                    new_node.appendChild(create_node(
                                        document.createTextNode(data.substr(
                                            0, result+Stxt.length))));
                    data = data.substr(result + Stxt.length);
                    data_low = data_low.substr(result + Stxt.length);
                }
                // while ((result = data_low.indexOf(Stxt)) != -1) {
                //     new_node.appendChild(document.createTextNode(
                //                             data.substr(0, result)));
                //     new_node.appendChild(create_node(
                //                         document.createTextNode(data.substr(
                //                             result, Stxt.length))));
                //     data = data.substr(result + Stxt.length);
                //     data_low = data_low.substr(result + Stxt.length);
                // }
                new_node.appendChild(document.createTextNode(data));
            }
        } else {
            // Keep going onto other elements!
            highlight(Stxt, node);
        }
    }
}
function create_node(child) {
    var node = document.createElement('span');
    node.setAttribute('class', 'highlighted');
    node.attributes['class'].value = 'highlighted';
    node.appendChild(child);
    return node;
}

// hide empty columns
$(document).ready(function() {
    $('#newterms').each(function(a, tbl) {
        var currentTableRows = document.getElementById('newterms').getElementsByTagName("tr").length-1;
        // console.log(currentTableRows);
        $(tbl).find('th').each(function(i) {
            var remove = 0;
            var currentTable = $(this).parents('table');
            // console.log(currentTable);
            var tds = currentTable.find('tr td:nth-child(' + (i + 1) + ')');
            // console.log(tds);
            tds.each(function(j) { if (this.innerHTML == '') remove++; });
            // console.log(remove);
            
            if (remove == currentTableRows) {
                $(this).hide();
                tds.hide();
            }
        });
    });

    // style the table
    $("#newterms").DataTable({
        // "pagingType": "full_numbers",
        "searching": false,
        "ordering":false,
        "scrollY": '500px',
        "scrollCollapse": true,
        "paging": false
        });
});

$(document).ready(function(){
    $(function() {
        var startX,
             startWidth,
             $handle,
             $table,
             pressed = false;
        
        $(document).on({
            mousemove: function(event) {
                if (pressed) {
                    $handle.width(startWidth + (event.pageX - startX));
                    console.log('move...')
                }
            },
            mouseup: function() {
                if (pressed) {
                    $table.removeClass('resizing');
                    pressed = false;
                }
            }
        }).on('mousedown', '.table-resizable th', function(event) {
            $handle = $(this);
            pressed = true;
            startX = event.pageX;
            startWidth = $handle.width();
            
            $table = $handle.closest('.table-resizable').addClass('resizing');
        }).on('dblclick', '.table-resizable thead', function() {
            // Reset column sizes on double click
            $(this).find('th[style]').css('width', '');
            // $(this).find('td[style]').css('width', '');
        });
    });
});
// insert javascript code here
// for the page

var async_counter = 0
var export_df = null
console.log("js file linked");

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function toggletabs(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  // document.getElementById("main-table_wrapper").style.display = "none";
  evt.currentTarget.className += " active";
}


function define_table_events() {
  // event handlers for generated table elements must be defined AFTER the elements are generated
  $(".set-fav").change(function () {
    console.log("checkbox detected")
    row_database_id = $(this).val();
    if (this.checked) {
      if (sessionStorage.getItem("fav_list")) {
        fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));
        console.log(fav_id_array)
        fav_id_array.push(row_database_id);
      }
      else {
        fav_id_array = [row_database_id]
      }
    }
    else {
      fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));
      remove_at_index = jQuery.inArray(row_database_id, fav_id_array)
      if (remove_at_index != -1) { // if a result is found
        fav_id_array.splice(remove_at_index, 1);
      }


    }

    sessionStorage.setItem("fav_list", JSON.stringify(fav_id_array));
    console.log(sessionStorage.getItem("fav_list"))
  });

}

async function autoresolve_street_name(selected_street_name) {
  dropdown_column_names = ["street_name"] //specify all columns in dataset to pull unique values for
  town_name = $('#inputTown').val()
  street_name_filter_query = {}
  if ($('#inputTown').prop('selectedIndex') != 0) {
    street_name_filter_query = { "town": town_name }
  }

  output_json = await eel.get_dropdown_values("query_input", dropdown_column_names, street_name_filter_query)()
  populate_dropdown(output_json)

  $("#inputStreetName option").each(function () {
    option_val = $(this).val()
    if (option_val == selected_street_name) {
      $('#inputStreetName').val(option_val)
    }
  });
}

function clear_dropdown(element_identifier) {
  selector_div = $(element_identifier);
  selector_div.children('option').not('.placeholder').remove(); // clear all existing <option> elements in a dropdown
}

function retrieve_input_values() {
  console.log("Input detected")
  input_dict = {}
  is_filter = false // flag to indicate if any filtering is performed. if not, se input_dict to null TO PREVENT ERROR
  $('.data-query').each(function (index, element) { // iterates through every HTML element with the .data-query class value
    // refer to HTML to see what data-field and search-type means
    column_name = $(element).attr("data-field")
    search_type = $(element).attr("search-type")
    input_value = $(element).val()

    selected_index = $(element).prop('selectedIndex'); //check if the first value of a dropdown (the placeholder) is selected
    if (selected_index == 0) {
      input_value = ""
    }
    // console.log(column_name)
    // console.log($(element).val())
    // if(column_name in input_dict){

    // }
    if (input_value != "") {
      is_filter = true
    }
    input_dict[column_name] = { "value": input_value, "search_type": search_type }

  });

  if (!is_filter) { // if no filtering is done (e.g load all results when webpage opens)
    input_dict = null
  }
  return input_dict
}

async function query_data() {
  //placeholder_str = "-- Any --"
  input_dict = retrieve_input_values()

  console.log(input_dict)
  console.log(typeof input_dict)
  datatable = $('#main-table').DataTable();
  datatable.clear().draw(); // clear all data on table
  console.log("datatable cleared")

  async_counter += 1 // flag to indicate if there are running async functions
  let df = await eel.query_db(input_dict)()

  async_counter -= 1
  if (df === undefined || df.length == 0) {
    //no results
    alert("No results found! Try another query.")
    return null
  }

  export_df = df
  console.log(df)
  console.log(typeof df)
  // //let df = await eel.query_csv(input_dict)()
  


  console.log(df)
  console.log(Object.keys(df).length)

  console.log(async_counter)
  if (async_counter == 0) { // if there are no pending async functions still running (i.e. it is the last one)
    fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));
    for (row_id in df) {

      // if (Object.keys(df[row_id]).length == column_count) { // check if the number of values in a row matches the number of columns. just in case.
      checked_html = " "
      if (fav_id_array && fav_id_array.includes(df[row_id]['_id']['$oid'])) {
        checked_html = " checked"
      }

      table_values = [`<td><input class="form-check-input set-fav" type="checkbox" value=${df[row_id]['_id']['$oid']}${checked_html}></td>`]
      for (var key of Object.keys(df[row_id])) {
        //console.log(key + " -> " + df[0][key])
        //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
        if (!(key.startsWith("_"))) {
          table_values.push(df[row_id][key])
        }

      }
      table_values.push(`<td><button id="${df[row_id]['_id']['$oid']}" onclick= "sendToView(this.id);">View</button></td>`)
      datatable.row.add(table_values);//add a row
      // }
    }
    datatable.draw();
    console.log("datatable populated")
    define_table_events()

    // this section of code is for autoresolving the selected town name if the user
    // selects the street_name directly
    street_name_selected_index = $('#inputStreetName').prop('selectedIndex');
    // town_selected_index = $('#inputTown').prop('selectedIndex');
    if (street_name_selected_index != 0) { // so long as the street_name is selected, autoresolve town value
      $('#inputTown').val(df[0]["town"]);
      autoresolve_street_name();
    }

  }

}



function populate_dropdown(dropdown_json) {
  //this function takes all unique values of a specified column in a JSON object from eel.get_dropdown_values(),
  //with the general format { key_name : [unique_value1, unique_value2] }
  // and sets them all into the respective <select> elements
  console.log("populating dropdown")
  console.log("dropdown values")
  console.log(dropdown_json)
  console.log(typeof dropdown_json)

  query_mode = dropdown_json["query_mode"]
  delete dropdown_json["query_mode"];

  for (var key of Object.keys(dropdown_json)) { // for every selected column to get dropdown values for

    selector_div = $(`.${query_mode} select[data-field=${key}]`)
    dropdown_json[key].sort()
    for (var index in dropdown_json[key]) { // iterate through every value listed under the column name

      if (key == "month") {
        // $("#inputEarliestDate").append(`<option>${dropdown_json[key][index]}</option>`);
        // $("#inputLatestDate").append(`<option>${dropdown_json[key][index]}</option>`);
        $( `.${query_mode} select[data-field*=${key}]` ).append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else {

        selector_div.append(`<option>${dropdown_json[key][index]}</option>`);
      }


      // if (key == "flat_type"){
      //   $( "#inputFlatType" ).append(`<option>${dropdown_json[key][index]}</option>`);
      // }
      // else if (key == "town"){
      //   $( "#inputTown" ).append(`<option>${dropdown_json[key][index]}</option>`);
      // }
      // else if (key == "street_name"){
      //   $( "#inputStreetName" ).append(`<option>${dropdown_json[key][index]}</option>`);
      // }
      // else if (key == "flat_model"){
      //   $( "#inputFlatModel" ).append(`<option>${dropdown_json[key][index]}</option>`);
      // }
      // else if (key == "month"){
      //   $( "#inputEarliestDate" ).append(`<option>${dropdown_json[key][index]}</option>`);
      //   $( "#inputLatestDate" ).append(`<option>${dropdown_json[key][index]}</option>`);

      // }
    }
  }

}

function populate_main_table(df) {
  export_df = df
  console.log("populating main table")
  console.log(df)
  console.log(typeof df)

  console.log(df[0])
  column_count = 0 // number of columns to show up on table
  //exclude_column_count = 0 // number of columns to hide from table. value used to offset condition to check if a row has the right number of column values 
  column_header_list = []

  //hide loading animation before table populated
  $(".loader").hide();


  //generate headers
  $("#main-table thead tr").append(`<th>Set Favourite</th>`); // column to add set favourite button
  for (var key of Object.keys(df[0])) {
    //console.log(key + " -> " + df[0][key])
    if (!(key.startsWith("_"))) {  // append column header
      column_header_list.push(key)
      column_count += 1
      $("#main-table thead tr").append(`<th>${key}</th>`);
    }
    // else{
    //   exclude_column_count += 1
    // }
  }
  $("#main-table thead tr").append(`<th>View</th>`);

  //populate table with data
  fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));
  checked_html = " "


  for (row_id in df) {
    if (fav_id_array && fav_id_array.includes(df[row_id]['_id']['$oid'])) {
      checked_html = " checked"
    }
    else {
      checked_html = " "
    }
    // if ((Object.keys(df[row_id]).length) == column_count) {
    // just to check if the number of items in the record matches the number of columns on the table

    // table_values_html = `<td style='display:none;'>${df[row_id]['_id']}</td>`
    table_values_html = `<td><input class="form-check-input set-fav" type="checkbox" value=${df[row_id]['_id']['$oid']}${checked_html}></td>`
    for (var key of column_header_list) {
      //console.log(key + " -> " + df[0][key])
      //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
      table_values_html += `<td>${df[row_id][key]}</td>`
    }

    table_values_html += `<td><button id="${df[row_id]['_id']['$oid']}" onclick= "sendToView(this.id);">View</button></td>`
    $("#main-table tbody").append(`<tr>${table_values_html}</tr>`);//add a row

    // }
  }

  main_table = $('#main-table').DataTable({
    // "createdRow": function( row, data, dataIndex){
    //     console.log(row)
    //     console.log(data)
    //     console.log(dataIndex)
    //     extracted_id = data[0].split('value=\"').pop();

    // },
    "pagingType": "input", //sets pagination mode
    order: [[0, 'desc']], // sets first column as descending
    language: {
      searchPlaceholder: "",
      search: "Filter existing results by text/number: ",
      "paginate": {
        "first": "First",
        "last": "Last",
        "next": "Next page >>",
        "previous": "Previous page <<"
      },
    }
  }); //datatable is declared only when the HTML for the table has been finalised

  $('#main-table').toggle(); //set table to visible
  define_table_events()

}

async function display_graphs(graph_url_json){

  console.log(graph_url_json)
  if (graph_url_json != null){
    
    for (var key of Object.keys(graph_url_json)){
      console.log(key)
      graph_category = key.slice(0, key.lastIndexOf('_'))
      split_index = key.slice(key.lastIndexOf('_') + 1)

      // $(`.${graph_category} img`).each(function(){ // clear all existing graphs
      //   $(this).remove()
      // })
      console.log(`#${graph_category}_graph_${split_index}`)
      //graph_div = $(`#${graph_category}_graph_${split_index} .graph_div`) // get jquery object of div to add graph in
      graph_div = $(`#${graph_category}_graph_${split_index}`)
      // graph_div.attr("src",`${graph_url_json[key]}`);
      console.log("appending")
      // html_code = `
      //   <iframe width="900" height="800" frameborder="0" scrolling="no" class="embed-responsive-item" id="${key}" src="${graph_url_json[key]}"></iframe>
      // `
      url = graph_url_json[key].replace("web/", "")
      timestamp = new Date().getTime();
      html_code = `
      <div class="container ${key}">
        <a style="display: block;" href="${url + ".html"}" class="link-primary" target="_blank">Click here to interact with the graph!</a>
        <img style="width: 80%;" class="img-fluid" id="${key}" src="${url + ".png?t=" + timestamp}" />
      </div>
      `
      $(`.${key}`).remove();
      console.log(html_code)
      graph_div.append(html_code)
      // await $("#test").prepend(html_code)
      
      iframe = $(`#${key}`);
      
      // while (delay){
      //   console.log("waiting")
      // }
      // console.log("appended")
      
      console.log(key)
      
    }
    
  }
  
}

async function set_visible_graphs(){
  // displayed_graphs = $("#setDisplayedGraphs").val()
  // if (displayed_graphs != "none"){

  // }
  $("#setDisplayedGraphs option").each(function() // loop through all graph categories
  {
      if ($(this).is(':selected')){ // if graph category is selected, run setup code, then set it to visible
        // initialise graphs
        query_dict = { "graph_category" : $(this).val() }
        cont = true
        graph_counter = 0

        while (cont){
          graph_element = $(`.${$(this).val()} div[graph-number=${graph_counter}]`) // for each graph element
          query_dict[graph_counter] = {}
          if (graph_element.length > 0){ // if a div with the correct graph number is found
            dropdown_element = graph_element.find('select');
            dropdown_element.each(function( index, selector ) { // for each dropdown value detected within a graph element
              // console.log( index + ": " + $( this ).text() );
              query_name = $(selector).attr("query-name")
              input_value = $(selector).val()
              console.log(query_name)
              console.log(input_value)
              query_dict[graph_counter][query_name] = input_value


            });
            graph_counter++ 
          }
          else{
            break;
          }
        }
        console.log(query_dict)

        graph_urls = eel.query_graphs(query_dict)(display_graphs)

        $(`.${$(this).val()}`).css("display", "block");
      }
      else{
        $(`.${$(this).val()}`).css("display", "none");
      }
  });
}

async function setup_graph(){
  console.log("initialising graph controls")
  dropdown_column_names = ["year_limit_5", "flat_type", "town"]
  let result = await eel.get_dropdown_values("graph_input", dropdown_column_names, {})()

  populate_dropdown(result)
  n = 'target_flat_type'
  $(`#trends_graph_1_flat_type option`).eq(2).prop('selected', true);
  set_visible_graphs()

}

function downloadCSV() {
  // eel.csvFormat(export_df);
  input_dict = retrieve_input_values()

  eel.query_db(input_dict, 0, true)()
}

//EVENT LISTENERS
$(document).ready(function () { // runs when the webpage loads
  console.log("document ready")
  $("#graph").css("display", "none")
  dropdown_column_names = ["flat_type", "town", "street_name", "flat_model", "month"] //specify all columns in dataset to pull all unique values for
  eel.get_dropdown_values("query_input", dropdown_column_names, {})(populate_dropdown)

  eel.query_db(null)(populate_main_table)
  setup_graph()
  // toggletabs();
  // eel.get_main_graphs()()

  //remove the line below to allow persistence through page refreshes
  // sessionStorage.clear() 
});

$("#inputTown").on("input", function () {
  //every time a town is chosen, filter the street_name dropdown to only 
  //show values found with the same town value
  selected_index = $('#inputTown').prop('selectedIndex'); //check if the first value of a dropdown (the placeholder) is selected
  if (selected_index != 0) { // if the user actually selected a town and not the placeholder
    clear_dropdown(`select[data-field="street_name"]`)
    selected_street_name = $('#inputStreetName').val()
    autoresolve_street_name(selected_street_name)
  }
  else if (selected_index == 0 && $('#inputStreetName').prop('selectedIndex') != 0) {
    // $('#inputStreetName').prop('selectedIndex', 0);
    clear_dropdown(`select[data-field="street_name"]`)
    autoresolve_street_name()
  }


});


$("#setDisplayedGraphs").on("input", function () {

  set_visible_graphs()
});

$(".data-query").on("input", function () {
  //every time an input is detected, run query
  //can consider a delay so that a query isnt run every letter (assuming this is even an issue)
  query_data()


});

$(".graph-query").on("input", function() {
  id_value = $(this).attr('id')
  parent_elem = $(this).closest('div[graph-number]')
  graph_num = parent_elem.attr('graph-number')
  parent_id = parent_elem.attr('id')
  graph_category = parent_id.slice(0, parent_id.lastIndexOf("_graph_"))
  query_dict = { "graph_category" : graph_category }
  query_dict[graph_num] = {} // store query values
  dropdown_element = parent_elem.find('select');
  dropdown_element.each(function( index, selector ) { // for each dropdown value detected within a graph element
    // console.log( index + ": " + $( this ).text() );
    query_name = $(selector).attr("query-name")
    input_value = $(selector).val()
    query_dict[graph_num][query_name] = input_value


  });
  console.log(query_dict)
  eel.query_graphs(query_dict)(display_graphs)

});


function sendToView(clicked_id) {
  window.location.href = 'view.html?recordId=' + clicked_id;
}
// function viewMap() {

//   image = eel.displaymap();
//   document.getElementById('imagestore').innerHTML = "<img src='" + image + "' />";
// }

// function toggletabs() {
//   // $('#graph').hide()
//   $('#graph_display').click(function () {
//     $("#main-table").hide();
//     $(".tab-content").hide();
//     $("#graph").show();
//   });
//   $("#main_table").click(function () {
//     $("#main-table").show();
//     $(".tab-content").show();
//   });

// }




// $("#inputStreetName").on("input", function() {
//   //every time a town is chosen, filter the street_name dropdown to only
//   //show values found with the same town value
//   console.log("detected1")
//   selected_index = $('#inputStreetName').prop('selectedIndex'); //check if the first value of a dropdown (the placeholder) is selected
//   if (selected_index != 0){ // if the user actually selected something and not the placeholder
//     // dropdown_column_names = ["street_name"] //specify all columns in dataset to pull unique values for
//     // town_name = $('#inputTown').val()
//     // street_name_filter_query = {"town": town_name}
//     // eel.get_dropdown_values(dropdown_column_names, street_name_filter_query)(populate_dropdown)
//     console.log("detected2")
//     target_dropdown_id = "#inputTown"
//     column_name = $(target_dropdown_id).attr("data-field")
//     user_selected_value = $(target_dropdown_id).val()
//     query_dict = { column_name : user_selected_value }
//     auto_select_dropdown(query_dict, target_dropdown_id)
//   }

// });

// next move most likely is to split the input for the numerical column searches to accept 2 values (to form a range)

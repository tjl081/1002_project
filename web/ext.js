// insert javascript code here
// for the page

var async_counter = 0

console.log("js file linked");


async function query_data() {
  //placeholder_str = "-- Any --"
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

  console.log(input_dict)
  console.log(typeof input_dict)
  datatable = $('#main-table').DataTable();
  datatable.clear().draw(); // clear all data on table
  console.log("datatable cleared")

  async_counter += 1 // flag to indicate if there are running async functions
  let df = await eel.query_db(input_dict)()
  console.log(df)
  console.log(typeof df)
  // //let df = await eel.query_csv(input_dict)()
  async_counter -= 1


  console.log(df)
  console.log(Object.keys(df).length)

  if (async_counter == 0) { // if there are no pending async functions still running (i.e. it is the last one)
    for (row_id in df) {

      if (Object.keys(df[row_id]).length == column_count) { // check if the number of values in a row matches the number of columns. just in case.

        table_values = []
        for (var key of Object.keys(df[row_id])) {
          //console.log(key + " -> " + df[0][key])
          //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
          table_values.push(df[row_id][key])
        }
        datatable.row.add(table_values);//add a row
      }
    }
    datatable.draw();
    console.log("datatable populated")
  }


}


function populate_dropdown(dropdown_json) {
  //this function gets all unique values of a specified column, then compiles them in a JSON object,
  //with the general format { key_name : [unique_value1, unique_value2] }
  console.log("populating dropdown")
  console.log("dropdown values")
  console.log(dropdown_json)
  console.log(typeof dropdown_json)

  for (var key of Object.keys(dropdown_json)) {

    dropdown_json[key].sort()
    for (var index in dropdown_json[key]) {
      if (key == "flat_type") {
        $("#inputFlatType").append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "town") {
        $("#inputTown").append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "street_name") {
        $("#inputStreetName").append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "flat_model") {
        $("#inputFlatModel").append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "month") {
        $("#inputEarliestDate").append(`<option>${dropdown_json[key][index]}</option>`);
        $("#inputLatestDate").append(`<option>${dropdown_json[key][index]}</option>`);

      }
    }
  }

}


function populate_main_table(df) {

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

  for (row_id in df) {

    if ((Object.keys(df[row_id]).length) == column_count) {
      // just to check if the number of items in the record matches the number of columns on the table

      table_values_html = ""
      for (var key of column_header_list) {
        //console.log(key + " -> " + df[0][key])
        //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
        table_values_html += `<td>${df[row_id][key]}</td>`
      }

      table_values_html += `<td><button onclick= "sendToView();">View</button></td>`
      $("#main-table tbody").append(`<tr>${table_values_html}</tr>`);//add a row

    }
  }

  main_table = $('#main-table').DataTable({
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

}

function displaygraph() { //prediction graph
  eel.heatmap_plot();
  $('#graph').append(`<img src= "/resources/heatmap.jpg">`);
}

//EVENT LISTENERS

$(document).ready(function () { // runs when the webpage loads
  console.log("document ready");
  dropdown_column_names = ["flat_type", "town", "street_name", "flat_model", "month"] //specify all columns in dataset to pull all unique values for
  eel.get_dropdown_values(null, dropdown_column_names)(populate_dropdown)
  console.log(1)
  eel.query_db(null)(populate_main_table)
  // toggletabs();
  displaygraph();
  console.log(2)
});

$(".data-query").on("input", function () {
  //every time an input is detected, run query
  //can consider a delay so that a query isnt run every letter (assuming this is even an issue)
  query_data()

  //contain_values = df[df['month'].str.contains('ju')]

});

function sendToView() {
  window.location.href = 'view.html';
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


// next move most likely is to split the input for the numerical column searches to accept 2 values (to form a range)

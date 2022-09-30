// insert javascript code here
// for the page

var async_counter = 0

console.log("js file linked");

eel.expose(say_hello_js); // Expose this function to Python
function say_hello_js(x) {
  console.log("Hello from " + x);
}


async function query_data(){
  //placeholder_str = "-- Any --"
  console.log("Input detected")
  input_dict = {}
  $('.data-query').each(function(index, element) {
    column_name = $(element).attr("data-field")
    input_value = $(element).val() 

    selected_index = $(element).prop('selectedIndex');
    if (selected_index == 0){
      input_value = ""
    }
    // console.log(column_name)
    // console.log($(element).val())
    
    input_dict[column_name] = input_value

  });
  console.log(input_dict)
  console.log(typeof input_dict)
  datatable = $('#main-table').DataTable();
  
  async_counter += 1
  let df = await eel.query_csv(input_dict)()
  async_counter -= 1

  datatable.clear().draw();
  console.log("datatable cleared")
  console.log(df)
  console.log(Object.keys(df).length)

  if (async_counter == 0){ // if there are no pending async functions
    for (row_id in df){
        
        if (Object.keys(df[row_id]).length == column_count){

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


async function populate_dropdown() { 
  //this function gets all unique values of a specified column, then compiles them in a JSON object,
  //with the general format { key_name : [unique_value1, unique_value2] }

  dropdown_column_names = ["flat_type", "town", "street_name", "flat_model" ] //specify all columns in dataset to pull all unique values for
  let dropdown_json = await eel.get_dropdown_values(null, dropdown_column_names)()
  console.log(dropdown_json)
  console.log(typeof dropdown_json)

  for (var key of Object.keys(dropdown_json)) {
    
    console.log(dropdown_json["flat_type"])
    dropdown_json[key].sort()
    for (var index in dropdown_json[key]){
      if (key == "flat_type"){
        $( "#inputFlatType" ).append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "town"){
        $( "#inputTown" ).append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "street_name"){
        $( "#inputStreetName" ).append(`<option>${dropdown_json[key][index]}</option>`);
      }
      else if (key == "flat_model"){
        $( "#inputFlatModel" ).append(`<option>${dropdown_json[key][index]}</option>`);
      }
    }
      }
  

  

}


async function populate_main_table() {

  
  let df = await eel.query_csv()()  // returns list of JSON object, each representing a row in the csv (key=column name) 
  console.log(df)
  console.log(typeof df)

  //generate headers
  for (var key of Object.keys(df[0])) {
    //console.log(key + " -> " + df[0][key])
    $( "#main-table thead tr" ).append(`<th>${key}</th>`);
      }

  column_count = Object.keys(df[0]).length

  for (row_id in df){
    
      if (Object.keys(df[row_id]).length == column_count){

        table_values_html = ""
        for (var key of Object.keys(df[row_id])) {
          //console.log(key + " -> " + df[0][key])
          //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
          table_values_html += `<th>${df[row_id][key]}</th>`
        }
        $( "#main-table tbody" ).append(`<tr>${table_values_html}</tr>`);//add a row
      }
  }

  main_table = $('#main-table').DataTable({ language: {
      "dom": '<"top"i>rt<"bottom"><"clear">',
      searchPlaceholder: "",
      search: "Filter existing results by text/number: ",
    }
  }); //datatable is declared only when the HTML for the table has been finalised
  $('#main-table').toggle();

}

say_hello_js("Javascript World!"); // output shows on browser side since this is just a javascript function
eel.say_hello_py("Javascript World!2"); // Call a Python function. output displays on python side



//EVENT LISTENERS

$(document).ready( function () {
  
  populate_dropdown()
  populate_main_table()
  
} );


$(".data-query").on("input", function() {
  //every time an input is detected, run query
  //can consider a delay so that a query isnt run every letter (assuming this is even an issue)
  query_data()
  
  //contain_values = df[df['month'].str.contains('ju')]



});


// next move most likely is to split the input for the numerical column searches to accept 2 values (to form a range)
// 
// insert javascript code here
// for the page



console.log("js file linked");

eel.expose(say_hello_js); // Expose this function to Python
function say_hello_js(x) {
  console.log("Hello from " + x);
}


async function populate_dropdown() { 
  //this function gets all unique values of a specified column, then compiles them in a JSON object,
  //with the general format { key_name : [unique_value1, unique_value2] }

  dropdown_column_names = ["flat_type", "town", "street_name", "flat model" ] //specify all columns in dataset to pull all unique values for
  let dropdown_json = await eel.get_dropdown_values(null, dropdown_column_names)()
  console.log(dropdown_json)
  console.log(typeof dropdown_json)
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
      searchPlaceholder: "Search text",
      search: "Search any column:",
    }
  }); //datatable is declared only when the HTML for the table has been finalised
  $('#main-table').toggle();

}

say_hello_js("Javascript World!"); // output shows on browser side since this is just a javascript function
eel.say_hello_py("Javascript World!2"); // Call a Python function. output displays on python side


$(document).ready( function () {
  
  populate_dropdown()
  populate_main_table()
  
} );


// currently assigning a df to a javascript var seems unfeasible (it is null)
// consider keeping running logic such that onstart/onlick -> python load df -> how to make python print out table
// need to see the most efficient way to populate a javascript table
//test if values are returned properly in the first place
//possible to convert a df to a json array?

//settle the progress report first
//and i dobnt think you submitted math tutorial or did qn 6 lol
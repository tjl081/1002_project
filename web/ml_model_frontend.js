console.log("ml model js file linked");

function populate_dropdown(dropdown_json) { 
    //this function gets all unique values of a specified column, then compiles them in a JSON object,
    //with the general format { key_name : [unique_value1, unique_value2] }
    console.log(dropdown_json)
    query_mode = dropdown_json["query_mode"]
    delete dropdown_json["query_mode"];
    
    for (var key of Object.keys(dropdown_json)) { // for every selected column to get dropdown values for
  
      selector_div = $(`.${query_mode} select[data-field=${key}]`)
      dropdown_json[key].sort()
      for (var index in dropdown_json[key]){ // iterate through every value listed under the column name
        
        if (key == "month"){
          // $( "#inputEarliestDate" ).append(`<option>${dropdown_json[key][index]}</option>`);
          // $( "#inputLatestDate" ).append(`<option>${dropdown_json[key][index]}</option>`);
          $( `.${query_mode} select[data-field*=${key}]` ).append(`<option>${dropdown_json[key][index]}</option>`);
        }
        else{
          selector_div.append(`<option>${dropdown_json[key][index]}</option>`);
        }
      }
    }
  
  }

async function predict_resale_values(housing_data){

  for (val of Object.values(housing_data)){
    if ( val == null || !val){
      $("#prediction_output").text("Please ensure all input boxes are properly filled")
      return null
    }
  }

  result = await eel.get_predicted_value(housing_data)()
  console.log(result)
  if (!isNaN(result)){  //https://stackoverflow.com/questions/175739/how-can-i-check-if-a-string-is-a-valid-number
    result = result.toLocaleString(
    undefined, // leave undefined to use the visitor's browser 
                // locale or a string like 'en-US' to override it.
    { maximumFractionDigits: 2 }
  ); // https://stackoverflow.com/questions/5731193/how-to-format-numbers
  $("#prediction_output").text("The predicted price of the flat is: $" + result)
  }
    
    
}

async function generate_graph(housing_data){
    $(".prediction_graph_container > .loader").show();
    result = await eel.get_prediction_graph(housing_data, 3)()
    $(".prediction_graph_container > .loader").hide();
    console.log(result)
    url = result.replace("web/", "")
    timestamp = new Date().getTime();
    $("#prediction_graph").remove();
    // html_code = `<img style="width: 80%;" class="img-fluid" id="prediction_graph" src="${url + "?t=" + timestamp}" />`
    html_code = `
      <a style="display: block;" href="${url + ".html"}" class="link-primary" target="_blank">Click here to interact with the graph!</a>
      <a href="${url + ".html"}" target="_blank"><img style="width: 80%;" class="img-fluid" id="prediction_graph" src="${url + ".png?t=" + timestamp}" /></a>
      `
    $(".prediction_graph_container").prepend(html_code)
    // $("#prediction_graph").attr("src",result);
    // $("#prediction_output").text("The predicted price of the flat is:" + result)
}


function enable_predict_button(){
    $(".ml_button").prop('disabled', false);
    $("#prediction_output").text("Machine learning module finished training.")

    
}


function retrieve_field_values(){
  // test_data = [{
    //     "month" : "2019-05",
    //     "town": "ANG MO KIO",
    //     "flat_type": "5 ROOM",
    //     "block": "351",
    //     "street_name": "ANG MO KIO ST 32",
    //     "storey_range": "13 TO 15",
    //     "floor_area_sqm": "110",
    //     "flat_model": "IMPROVED",
    //     "lease_commence_date": "2001",
    //     "remaining_lease": "81 years 04 months"
    // }]

    data_template = {
      "month" : null,
      "town": null,
      "flat_type": null,
      "block": null,
      "street_name": null,
      "storey_range": null,
      "floor_area_sqm": null,
      "flat_model": null,
      "lease_commence_date": null,
      "remaining_lease": null
  }

  input_data = {}

  $('.data-query').each(function(index, element) {
      // refer to HTML to see what data-field and search-type means
      column_name = $(element).attr("data-field") 
      input_value = $(element).val()

      selected_index = $(element).prop('selectedIndex'); //check if the first value of a dropdown (the placeholder) is selected
      if (selected_index == 0) {
        input_value = ""
      }

      input_data[column_name] = input_value
  })
  input_data["month"] = input_data["date_year"] + "-" + input_data["date_month"]
  input_data["lease_commence_date"] = parseInt(input_data["remaining_lease"]) + parseInt(input_data["date_year"]) - 99

  input_data["storey_range"] = input_data["storey_range_min"] + " TO " + input_data["storey_range_max"]

  delete input_data["date_year"]
  delete input_data["date_month"]
  delete input_data["storey_range_min"]
  delete input_data["storey_range_max"]
  input_data = Object.assign(data_template, input_data)
  console.log(input_data)
  return input_data
}

$(document).ready( function () { // runs when the webpage loads
    
    dropdown_column_names = ["flat_type", "town", "street_name", "flat_model", "month" ] //specify all columns in dataset to pull all unique values for
    eel.get_dropdown_values("query_input", dropdown_column_names, {})(populate_dropdown)
    eel.init_ml_model()(enable_predict_button)
    $("#prediction_output").text("Loading machine learning module. In the meantime, please input the resale flat data you wish to predict the price of.")

  } );


$("#init_ml_model").on("click", function() {
    
    values = retrieve_field_values()
    predict_resale_values(values)
    
  });

$("#get_ml_graph").on("click", function() {
  values = retrieve_field_values()
  generate_graph(values)
})
  
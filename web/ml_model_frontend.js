console.log("ml model js file linked");

function populate_dropdown(dropdown_json) { 
    //this function gets all unique values of a specified column, then compiles them in a JSON object,
    //with the general format { key_name : [unique_value1, unique_value2] }
    for (var key of Object.keys(dropdown_json)) {
      
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

async function predict_resale_values(housing_data){
    result = await eel.get_predicted_value(housing_data)()
    console.log(result)
    $("#prediction_output").text("The predicted price of the flat is:" + result)
    
}

async function generate_graph(housing_data){
    result = await eel.get_prediction_graph(housing_data, 3)()
    console.log(result)
    $("#prediction_graph").attr("src",result);
    // $("#prediction_output").text("The predicted price of the flat is:" + result)
}


function enable_predict_button(){
    $(".ml_button").prop('disabled', false);
    
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
    eel.get_dropdown_values(null, dropdown_column_names)(populate_dropdown)
    eel.init_ml_model()(enable_predict_button)


  } );


$("#init_ml_model").on("click", function() {
    
    values = retrieve_field_values()
    predict_resale_values(values)
    
  });

$("#get_ml_graph").on("click", function() {
  values = retrieve_field_values()
  generate_graph(values)
})
  
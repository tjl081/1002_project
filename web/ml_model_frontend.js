console.log("ml model js file linked");


async function predict_resale_values(housing_data){
    result = await eel.get_predicted_value(housing_data)()
    return result
}

$(document).ready( function () { // runs when the webpage loads
    eel.init_ml_model()

  } );


$("#init_ml_model").on("click", function() {
    
    test_data = [{
        "month" : "2019-05",
        "town": "ANG MO KIO",
        "flat_type": "5 ROOM",
        "block": "351",
        "street_name": "ANG MO KIO ST 32",
        "storey_range": "13 TO 15",
        "floor_area_sqm": "110",
        "flat_model": "IMPROVED",
        "lease_commence_date": "2001",
        "remaining_lease": "81 years 04 months"
    }]

    result = predict_resale_values(test_data)
    console.log(result)
  
  });
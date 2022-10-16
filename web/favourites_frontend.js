

var export_df = null


function define_table_events(){

    $(".remove-result").on("click", function() {
        fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));      
        obj_id = $(this).attr('data-value')
        console.log(obj_id)
        remove_at_index = jQuery.inArray(obj_id, fav_id_array)
        console.log(remove_at_index)
        
        if (remove_at_index != -1){
            remove_at_index = jQuery.inArray(obj_id, fav_id_array)
            fav_id_array.splice(remove_at_index, 1);
        }

        $(this).parents().eq(1).remove()
        sessionStorage.setItem("fav_list", JSON.stringify(fav_id_array));
      });
}


async function populate_fav_table(fav_id_array){


    console.log(fav_id_array)
    if (fav_id_array && fav_id_array.length > 0){
        query_dict = { "_id" :{ "value": fav_id_array } }
        let df = await eel.query_db(query_dict)()
        export_df = df
        console.log(df)
        column_header_list = []

        //generate headers
        // $("#main-table thead tr").append(`<th>Set Favourite</th>`); // column to add set favourite button
        for (var key of Object.keys(df[0])) {
            //console.log(key + " -> " + df[0][key])
            if (!(key.startsWith("_"))) {  // append column header
            column_header_list.push(key)
            $("#main-table thead tr").append(`<th>${key}</th>`);
            }
            // else{
            //   exclude_column_count += 1
            // }
        }
        $("#main-table thead tr").append(`<th>   </th>`);

        main_table = $('#main-table').DataTable({
            // "createdRow": function( row, data, dataIndex){
            //     console.log(row)
            //     console.log(data)
            //     console.log(dataIndex)
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
            });


        //populate table
        for (row_id in df) { // for every table row

            // if (Object.keys(df[row_id]).length == column_count) { // check if the number of values in a row matches the number of columns. just in case.
    
        //   table_values = [`<td><input class="form-check-input set-fav" type="checkbox" value=${df[row_id]['_id']['$oid']}></td>`]
            table_values = []
        // for (var key of Object.keys(df[row_id])) {
        //     //console.log(key + " -> " + df[0][key])
        //     //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
        //     if (!(key.startsWith("_"))){
        //     table_values.push(df[row_id][key])
        //     }
        // }
            for (var key of column_header_list) {
                //console.log(key + " -> " + df[0][key])
                //$( "#main-table tbody tr" ).append(`<th>${df[row_id][key]}</th>`);
                table_values.push(df[row_id][key])
            }

            table_values.push(`<td><button class="btn btn-danger remove-result" data-value="${df[row_id]['_id']['$oid']}">Remove from favourites</button></td>`)
            main_table.row.add(table_values);//add a row
            // }
        }
        $('#main-table').toggle();
        $('#download-btn').toggle();
        main_table.draw();
        define_table_events()

    }
    else{
        alert("No favourites selected in main page")
    }
    
}


$(document).ready( function () { // runs when the webpage loads
    
    fav_id_array = JSON.parse(sessionStorage.getItem("fav_list"));
    populate_fav_table(fav_id_array)

  } );
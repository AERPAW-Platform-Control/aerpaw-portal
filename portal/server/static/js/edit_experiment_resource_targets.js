console.log('edit resource targets ')
function noVehiclesForFixedNode(){
    let nodeType = $('#resource_node_type')
    console.log(nodeType)
    if( $('#node_type').text() == 'afrn' ){
        $('#id_node_vehicle').find('option').each( (index, option) => {
            if( $(option).val() != 'vehicle_none' ){
                $(option).remove()
            }
        })

    }
}

noVehiclesForFixedNode()
function singleChoiceCheckBoxGroup(clickedCheckbox){
    let checkboxGroup = $(clickedCheckbox).parentsUntil('div.single-choice-checkbox-group').parent()
    $(checkboxGroup).find('input[type=checkbox]').each((checkboxIndex, checkbox)=>{
        if(checkbox != clickedCheckbox){
            $(checkbox).prop('checked', false)
        }
    })
}

function showNextGroup(button){
    console.log('button clicked', button)
    let hide = $(button).attr('data-hide')
    let target = $($(button).attr('data-target'))
    if(hide == 'true'){
        $(target).hide()
    }else if(hide == 'false'){
        $(target).show()
    }
}

$(document).ready(function (){
    $('input[type="checkbox"]').each((index, checkbox)=>{
        $(checkbox).on('click', ()=>{
            singleChoiceCheckBoxGroup(checkbox)
        })
    })
    

})
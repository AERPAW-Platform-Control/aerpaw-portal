
var singleChoiceCheckboxGroupCount = 0
var showNextGroupCount = 0
var toggleGroupCount = 0
var hideDescendingTargetGroupsCount = 0


function singleChoiceCheckBoxGroup(clickedCheckbox){
    singleChoiceCheckboxGroupCount += 1
    /*  
        Only allows for one checkbox in a group to be checked
        Unchecks other checkboxes in the group when another checkbox in the group is checked
        Grouped by: .single-choice-checkbox-group
    */
    let checkboxGroup = $(clickedCheckbox).parentsUntil('div.single-choice-checkbox-group').parent()
    $(checkboxGroup).find('input[type=checkbox]').each((checkboxIndex, checkbox)=>{
        if(checkbox != clickedCheckbox){
            
            console.log(`checkbox id = ${$(checkbox).attr('id')}`)
            let wasChecked = $(checkbox).prop('checked')
            if( $(checkbox).prop('checked') ){
                console.log(`${$(checkbox).attr('id')} checkbox is checked`)
                $(checkbox).prop('checked', false)
                if( $(checkbox).attr('onclick') == 'toggleGroup(this)' ){
                    if( wasChecked == true ){
                        toggleGroup(checkbox)
                    }
                }
            }
        }
    })
}

function showNextGroup(button){
    showNextGroupCount += 1
    /* 
        Shows the next targeted group of elements depending on the data-hide attribute of the button pressed
        Show: data-hide="false"
        Hide: data-hide="true"
        Target: data-target="<targeted element id with # at beginning>"
     */
    let target = $($(button).attr('data-target'))
        let hide = $(button).attr('data-hide')
        if( $(button).prop('checked') ){
            if(hide == 'true'){
                $(target).hide()
                $(target).find('input, textarea').each((index, input)=>{
                    $(input).attr({'data-validate':false})
                })
                clearInputGroup(target)
                hideDescendingTargetGroups(target)
            }else if(hide == 'false'){
                $(target).show()
                $(target).find('input, textarea').each((index, input)=>{
                    $(input).attr({'data-validate':true})
                })
            }
        } else {
            $(target).hide()
            clearInputGroup(target)
            hideDescendingTargetGroups(target)
            
        }
    }
    

function toggleGroup(button){
    toggleGroupCount += 1

    let target = $($(button).attr('data-target'))
    if( $(target).is(':hidden') == true ){
        $(target).show()
        
    } else {
        $(target).hide()
        
        clearInputGroup(target)
        hideDescendingTargetGroups(target)
    }
}

function hideDescendingTargetGroups(targetId){
    hideDescendingTargetGroupsCount += 1
    $(targetId).find('input').each((inputIndex, input) => {
        let onclickFun = $(input).attr('onclick')
        if( onclickFun == 'showNextGroup(this)' || onclickFun == 'toggleGroup(this)' ){
            let nextTarget = $(input).attr('data-target')
            $(nextTarget).hide()
            clearInputGroup(nextTarget)
        }
    })
}

function clearInputGroup(groupOfInputs){
    $(groupOfInputs).find('input').each((inputIndex, input) => {
        switch ( $(input).attr('type') ){
            case 'checkbox':
                $(input).prop('checked', false)
                break;
            default:
                $(input).val('')
        }
    })
}


function requireConsecutiveCheckboxes(checkbox){
    /* 
        Takes a checked checkbox
        Gets all checkboxes with same name attr
        **Checkboxes with same name must have an id that can be sorted
        Sorts them by id 
        If the checked checkbox IS NOT directly before or after the checked checkbox -> send error message
        If the checked checkbox IS directly before or after the checked checkbox -> return true
    */
    if($(checkbox).hasClass('consecutive-check') == true){
        let checkboxDate = $(checkbox).attr('data-date')
        checkboxFamilyName = $(checkbox).attr('name')
        siblingCheckboxes = Array.from(document.getElementsByName(checkboxFamilyName))
        siblingCheckboxes.sort((a,b)=>{
            const dateA = $(a).attr('data-date')
            const dateB = $(b).attr('data-date')
            if(dateA < dateB){
                return -1
            }
            if(dateA > dateB){
                return 1
            }
            return 0
        })
        let checkboxIndex = siblingCheckboxes.indexOf(checkbox)
        let checkedCheckboxes = siblingCheckboxes.filter(cb => cb.checked && !cb.disabled)
        let isConsecutive = true
        for(let i=1; i< checkedCheckboxes.length; i++){
            const currentIndex = siblingCheckboxes.indexOf(checkedCheckboxes[i])
            const prevIndex = siblingCheckboxes.indexOf(checkedCheckboxes[i-1])

            if(currentIndex !== prevIndex+1){
                isConsecutive = false
                break
            }
        }


        return isConsecutive
    }
}

function reservationLimit(calendarId, checkboxName, limit){
    let checkedCount = 0
    $(calendarId).find('input[type="checkbox"]').each((checkboxIndex, checkbox) => {
        if($(checkbox).attr('name') == checkboxName && $(checkbox).prop('checked') == true){
            checkedCount = checkedCount +1
        }
    })
    if(checkedCount > limit){
        return false
    } else if(checkedCount <= limit){
        return true
    }
}

function minDaysReserved(calendarId, checkboxName, min){
    let checkedCount = 0
    $(calendarId).find('input[type="checkbox"]').each((checkboxIndex, checkbox) => {
        if($(checkbox).attr('name') == checkboxName && $(checkbox).prop('checked') == true){
            checkedCount = checkedCount +1
        }
    })
    if(checkedCount < min){
        return false
    } else if(checkedCount >= min){
        return true
    }
}
function reservationErrorMsg(isMinReservation, isConsecutive, isWithinLimit){
    if( !isMinReservation ){
        $('#reservation-min-msg').addClass("text-bg-danger")
    }else{
        $('#reservation-min-msg').removeClass("text-bg-danger")
    }

    if( !isConsecutive ){
        $('#reservation-consecutive-msg').addClass('text-bg-danger')
    }else{
        $('#reservation-consecutive-msg').removeClass('text-bg-danger')
    }
    
    if( !isWithinLimit ){
        $('#reservation-limit-msg').addClass('text-bg-danger')
    }else{
        $('#reservation-limit-msg').removeClass('text-bg-danger')
    }
}

function enableReserveSandboxBtn(checkbox){
    let disableButton = true
    let isMinReservation = minDaysReserved('#sandbox-calendar', 'sandbox-calendar-day', 1)
    let isConsecutive = requireConsecutiveCheckboxes(checkbox)
    let isWithinLimit = reservationLimit('#sandbox-calendar', 'sandbox-calendar-day', 5)
    
    if( isConsecutive == false ){
        disableButton = true
    } else if( isWithinLimit == false ){
        disableButton = true
    } else if( isMinReservation == false ){
        disableButton = true
    } else {
        disableButton = false
    }

    reservationErrorMsg(isMinReservation, isConsecutive, isWithinLimit)
    $('button[name="b_sandbox_submit"]').prop('disabled', disableButton)
}

$(document).ready(function (){
    
    $('input[type="checkbox"]').each((index, checkbox)=>{
        /*  
            Only allows one chekbox in a group to be selected by
            unchecking other checkboxes in the group if another one is checked
        */
       $(checkbox).on('click', ()=>{
            if($(checkbox).hasClass('single-check')){
                    singleChoiceCheckBoxGroup(checkbox)
            }

            if($(checkbox).attr('name') == "sandbox-calendar-day" && $(checkbox).hasClass('consecutive-check')){
                    enableReserveSandboxBtn(checkbox)
               
            }
       })
    })

    

})

var singleChoiceCheckboxGroupCount = 0
var showNextGroupCount = 0
var toggleGroupCount = 0
var hideDescendingTargetGroupsCount = 0


function singleChoiceCheckBoxGroup(clickedCheckbox){
    singleChoiceCheckboxGroupCount += 1
    console.log(' ')
    console.log('SINGLE CHOICE CHECKBOX count= ', singleChoiceCheckboxGroupCount)
    console.log($(clickedCheckbox).siblings('label').text())
    /*  
        Only allows for one checkbox in a group to be checked
        Unchecks other checkboxes in the group when another checkbox in the group is checked
        Grouped by: .single-choice-checkbox-group
    */
    let checkboxGroup = $(clickedCheckbox).parentsUntil('div.single-choice-checkbox-group').parent()
    $(checkboxGroup).find('input[type=checkbox]').each((checkboxIndex, checkbox)=>{
        if(checkbox != clickedCheckbox){
            console.log(' A - singleChoiceCheckBoxGroup ')
            let wasChecked = $(checkbox).prop('checked')
            if( $(checkbox).prop('checked') ){
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
    console.log(' ')
    console.log('SHOW NEXT GROUP count= ', showNextGroupCount)
    console.log($(button).siblings('label').text())
    /* 
        Shows the next targeted group of elements depending on the data-hide attribute of the button pressed
        Show: data-hide="false"
        Hide: data-hide="true"
        Target: data-target="<targeted element id with # at beginning>"
     */
    let target = $($(button).attr('data-target'))
    console.log(' A - showNextGoup ')
        let hide = $(button).attr('data-hide')
        console.log('hide= ', hide)
        if( $(button).prop('checked') ){
            if(hide == 'true'){
                console.log(' B - showNextGoup ')
                $(target).hide()
                clearInputGroup(target)
                hideDescendingTargetGroups(target)
            }else if(hide == 'false'){
                console.log(' C - showNextGoup')
                $(target).show()
            }
        } else {
            console.log(' D - showNextGoup ')
            $(target).hide()
            clearInputGroup(target)
            hideDescendingTargetGroups(target)
            
        }
    }
    

function toggleGroup(button){
    toggleGroupCount += 1
    console.log(' ')
    console.log('TOGGLE GROUP count= ', toggleGroupCount)
    console.log($(button).siblings('label').text())

    let target = $($(button).attr('data-target'))
    if( $(target).is(':hidden') == true ){
        console.log(' A - toggleGroup ')
        $(target).show()
    } else {
        console.log(' A - toggleGroup ')
        $(target).hide()
        clearInputGroup(target)
        hideDescendingTargetGroups(target)
    }
}

function hideDescendingTargetGroups(targetId){
    hideDescendingTargetGroupsCount += 1
    console.log(' ')
    console.log(' HIDE DESCENDING TARGET GROUPS count=, ', hideDescendingTargetGroupsCount)
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
    console.log(' ')
    console.log('CLEAR INPUT GROUP')
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
        console.log('checkbox')
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
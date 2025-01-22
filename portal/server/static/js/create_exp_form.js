console.log('creat experiment form js')

function canonicalExperiment(){
    $('#expTypeCan').on('click', ()=>{
        if( $('#expTypeCan').prop('checked') ){
            $('#canonicalSubmit').show()
            $('#nonCanonicalSubmit').hide()
            requiredInput(isRequired = false)
        } else { 
            $('#canonicalSubmit').hide()
            $('#nonCanonicalSubmit').hide()
            requiredInput(isRequired = false)
        }

    })
}

function nonCanonicalExperiment(){
    $('#expTypeNon').on('click', ()=>{
        if( $('#expTypeNon').prop('checked') ){
            $('#canonicalSubmit').hide()
            $('#nonCanonicalSubmit').show()
            requiredInput(isRequired = true)
        } else {
            $('#canonicalSubmit').hide()
            $('#nonCanonicalSubmit').hide()
            requiredInput(isRequired = true)
        }
    })
}

function requiredInput(isRequired){
    const requiredInputs = [ $('#description'), $('#hardware'), $('#software'), ]
        requiredInputs.forEach((inp) => {
            $(inp).prop('required', isRequired)
        })
}

function validateForm(){
    let validForm = true
    let validTitle = min5CharacterAnswer('experimentTitle')
    let validDescription = min5CharacterAnswer('description')
    let validGoal = min5CharacterAnswer('goal')

    if(validTitle == false){
        $('#experimentTitle-message').remove()
        $('#experimentTitle').after("<p id='experimentTitle-message' class='text-danger'>*Must be greater than 5 characters long</p>")
        validForm = false
    }else{
        $('#experimentTitle-message').remove()
    }

    if(validDescription == false && document.getElementById('description').required == true){
        $('#description-message').remove()
        $('#description').after("<p id='description-message' class='text-danger'>*Must be greater than 5 characters long</p>")
        validForm = false
    }else if(validDescription == true && document.getElementById('description').required == true){
        $('#description-message').remove()
    }else if(document.getElementById('description').required == false){
        validDescription= true
    }

    if(validGoal == false){
        $('#goal-message').remove()
        $('#goal').after("<p id='goal-message' class='text-danger'>*Must be greater than 5 characters long</p>")
        validForm = false
    }else{
        $('#goal-message').remove()
    }
    console.log(`the form is valid: ${validForm}`)
    if(validTitle == true && validDescription == true && validGoal == true){
        validForm = true
        $('#canonicalSubmit').prop('disabled', false)
        $('#nonCanonicalSubmit').prop('disabled', false)
    }

    if(validForm == false){
        $('#canonicalSubmit').prop('disabled', true)
        $('#nonCanonicalSubmit').prop('disabled', true)
    }
}

function min5CharacterAnswer(inputId){
    let input = $(`#${inputId}`)
    let inputVal = $(`#${inputId}`).val()
    
    console.log(`${inputId} length= ${inputVal.length}`)
    if(inputVal.length <= 5 ){
        return false
    }else{
        return true
    }
}

canonicalExperiment()
nonCanonicalExperiment()
$('textarea').each((i,textarea)=>{
    $(textarea).on('input', () => {
        validateForm()
    })
})
$('input[type=text]').each((i,input)=>{
    $(input).on('input', () => {
        validateForm()
    })
})
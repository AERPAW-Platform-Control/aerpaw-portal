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

canonicalExperiment()
nonCanonicalExperiment()
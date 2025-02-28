class Experiment{

    constructor(input, is_checked, is_success, rescheduleTB, initDevelopment){
        this.id = $(input).val()
        this.element = input
        this.is_checked = is_checked
        this.success = is_success
        this.initDevelopment = initDevelopment
    }

    singleExpOnly(){
        $(allExperiments).each((index, exp) => {
            let expOptions = $(exp.element).parent('label').next('div').find('input[type=checkbox]')
            if( exp.id != this.id ){
                exp.is_checked = false
                $(exp.element).prop('checked', false)
                $(exp.element).parent('label').next('div').hide()
                $(expOptions).each((i, expOp) => {
                    $(expOp).prop('checked', false)
                })
                $(exp.element).parent('label').next('div').hide()
            }else if( exp.id == this.id ){
                exp.is_checked = true
                $(exp.element).parent('label').next('div').show()
            }
        })
    }
}

const allExperiments = []


$(document).ready(()=>{
    // Create Experiment instances
    $('input[name=experiment_form]').each((index, input) => {
        const newExperiment = new Experiment($(input), false, false, false, false)
        allExperiments.push(newExperiment)
        $(input).parent('label').next('div').find('input[name="is-success"]').val(newExperiment.id)
        $(input).parent('label').next('div').find('input[name=reschedule-testbed]').val(newExperiment.id)
        $(input).parent('label').next('div').find('input[name=init-development]').val(newExperiment.id)
    })


    // ON click
    $(allExperiments).each((index, input) => {
        $(input.element).on('click', ()=>{
            if($(input.element).prop('checked') == true){
                input.singleExpOnly()
            }else if($(input.element).prop('checked') == false){
                $(input.element).parent('label').next('div').hide()
                input.is_checked = false
            }
        })
    })
})
console.log('create experiment form js')


class FormMessage{
    static allMessages = []
    constructor(id, parentElement, message,){
        this.id=id
        this.parent=parentElement
        this.message=message
        FormMessage.allMessages.push(this)
    }

    static init(form){
        let formContainer = $(form).find('div[name=create-exp-message]')
        let message = $(formContainer).find('p').each((index,message)=>{
            let name = $(message).attr('name')
            const form = new FormMessage(name, message, formContainer)

        })
    }

    static messageExists(messageId){
        let exists = $('#create-experiment').find(`#${messageId}`).length
        if(exists > 0){
            $(FormMessage.allMessages).each((message)=>{
                if(message.id == messageId){
                    return message
                }
            })
        }else{
            return false
        }
    }

    removeMessage(){
        $(this.message).remove()
        let indexToRemove = ''
        $(FormMessage.allMessages).each((index, message)=>{
            if(this == message){
                indexToRemove = index
                $(`#${this.id}`).remove()
            }
        })
        FormMessage.allMessages.splice(indexToRemove, 1)
    }


    
}

class FormInput{
    /*  
    - id: the input's id
    - input: input element
    - required: boolean if the input is required or optional
    - min5Char: boolean if the input requires a minimum of 5 characters
    - min5Met: boolean if the minimum of 5 charactersis met 
    */
   static allFormInputs = []

    constructor(input){
        this.input=$(input)
        this.type=$(input).attr('type') || 'textarea'
        this.id=$(input).attr('id')
        this.required=$(input).attr('required')
        this.min5Char=$(input).attr('data-five-chars') || false
        this.min5Met=false
        this.checked=$(input).prop('checked')||false
        this.isValidated=false
        this.validate=$(input).attr('data-validate') || true
        this.messages=[]
        FormInput.allFormInputs.push(this)
    }
    
    static init(form){
        
        // Create an instance for each input with type == text
        $(form).find('input').each((index, input)=>{
            if ($(input).attr('type') != 'checkbox'){
                const formInput = new FormInput($(input))
                formInput.validateThis()
            }
        })
        

        //Create an instance for each textarea
        $(form).find('textarea').each((index, textarea)=>{
            const formInput = new FormInput($(textarea))
            formInput.validateThis()
        })

        // Create an instance for each checkbox input and create a CheckBoxGroup for checkboxes that are part of the same question
        
        $(form).find('div[name="checkbox-container"]').each((index, checkboxContainer)=>{
            let checkboxes = []
            $(checkboxContainer).find('input[type="checkbox"]').each((index, checkbox)=>{
                const formInput = new FormInput($(checkbox))
                checkboxes.push(formInput)
            })
            const checkboxGroup = new CheckboxGroup($(checkboxContainer), checkboxes)
        })

    }

    static getInputById(id){
        let inputToGet
        $(FormInput.allFormInputs).each((index, input)=>{
            if(input.id == id){
                inputToGet = input
            }
        })
        return inputToGet
    }
    
    static getMultipleInputById(idList){
        let inputList = []
        $(idList).each((index, id)=>{
            let inputToGet = FormInput.allFormInputs.find(inp => inp.id === id)
            console.log(`inputToGet= ${inputToGet} ${inputToGet.id}`)
            inputList.push(inputToGet)
        })
        return inputList
    }

    validate5CharMin(){
        // Returns true if the input is greater than 5 characters or does not require a min character count
        // Returns false if the input does not meet its character count
        let inputVal = $(this.input).val()
        if($(this.input).attr('data-five-chars') == 'true'){
            if(inputVal.length < 5 ){
                return false
            }else{
                return true
            }
        }else{
            return true
        }
    }

    validateTextPresent(){
        // If the input has text in its value return true
        // If the input is blank return false
        let ans = ''
        if(this.type == 'text' || this.type == 'email'){
            ans = $(this.input).val()   
        }else if(this.type == 'textarea'){
            ans = $(this.input).text()
            
        }
        if(ans.trim() == ''){
            return false
        }else{
            return true
        }
    }  
    
    findCheckboxGroup(){
        // finds and returns the CheckboxGroup that a checkbox input belongs to
        if(this.type != 'checkbox'){
            return 'Error! Not a checkbox'
        }
        
        let inputGroup = ''
        $(CheckboxGroup.allGroups).each((i, group)=>{
            if(group.checkboxes.includes(this)){
                inputGroup = group
            }
        })
        return inputGroup
    }

    validateCheckBoxGroup(){
        let group = this.findCheckboxGroup()
        let checkedCount = 0
        for(let i=0; i < group.checkboxes.length; i++){
            if($(group.checkboxes[i].input).is(':checked')){
                checkedCount+=1
            }
        }
        if(checkedCount === 0){
            return false
        }else{
            return true
        }
    }

    determineChecked(){
        let group = this.findCheckboxGroup()
        $(group.checkboxes).each((index, checkbox)=>{
            // if the checkbox is the one that has been clicked
            // check if it is marked checked
            // change the object value - checked
            if(checkbox == this){
                console.log(`b checked= ${this.checked}`)
                if($(checkbox).is(':checked')){
                    this.checked = false
                }else{
                    this.checked = true
                }
                if( this.id == 'expTypeCan' && this.checked ){
                    FormButton.manageSubmitButtons(true)

                    /* Remove the asterisk next to the lead experimenter email input to signify it is not required for canonical experiments */
                    $("label[for='leadExperimenterEmail'] span").remove()
                }else if( this.id == 'expTypeNon' && this.checked ){
                    FormButton.manageSubmitButtons(false)

                    /* Add the asterisk next to the lead experimenter email to signify it is required for non-canonical experiments */
                    let asterisk = $("label[for='leadExperimenterEmail']").children('span')
                    if(asterisk.length == 0){
                        $("label[for='leadExperimenterEmail']").append('<span class="text-danger fs-4">*</span>')
                    }
                }
            }else{
                console.log(`c checked= ${this.checked}`)
                if($(checkbox).is(':checked')){
                    $(checkbox.input).prop('checked', false)
                    checkbox.checked = false
                }
            }
        })
    }

    messageExists(messageId){
        let exists = false
        if(this.type != 'checkbox'){
            $(this.messages).each((index, message)=>{
                if(message.id == messageId){ 
                    exists = true
                    return message
                }
            })
        }else if(this.type == 'checkbox'){
            let group = this.findCheckboxGroup()
            $(group.messages).each((index, message)=>{
                if(message.id == messageId){ 
                    exists = true
                    return message
                }
            })
        }
        if(exists == false){
            return false
        }
        
    }

    addRequiredMessage(){
        
        if(this.type != 'checkbox'){
            let messageId = `${this.id}-required`
            let exists = this.messageExists(messageId)
            if(exists == false){
                let message = `<p id="${messageId}" class="text-danger">This field is required</p>`
                const newMessage = new FormMessage(messageId, this.input, message)
                $(this.input).before(newMessage.message)
                this.messages.push(newMessage)
            }
        }else if(this.type == 'checkbox'){
            let group = this.findCheckboxGroup()
            let messageId = `${group.parentId}-required`
            let exists = this.messageExists(messageId)
            if( exists == false ){
                let message = `<p id="${messageId}" class="text-danger">This field is required</p>`
                const newMessage = new FormMessage(messageId, group.container, message)
                $(group.container).prepend(newMessage.message)
                group.messages.push(newMessage)
            }
        }
        
    }

    addMin5CharMessage(){
        let messageId = `${this.id}-min5`
        let message = `<p id="${messageId}" class="text-danger">This field requires an answer containing at least 5 characters.</p>`
        let exists = FormMessage.messageExists(messageId)
        if(exists == false){
            const newMessage = new FormMessage(messageId, this.input, message)
            if(this.type != 'checkbox'){
                $(this.input).before(newMessage.message)
                this.messages.push(newMessage)
            }
        }
    }

    addExpTypeMessage(){
        let messageId = `${this.id}-expType`
        let message = `<p id="${messageId}" class="text-danger">Please select an experiment type</p>`
        let exists = FormMessage.messageExists(messageId)
        if(exists == false){
            const newMessage = new FormMessage(messageId, this.input, message)
            if(this.type == 'checkbox' && this.id == 'expTypeCan' || this.id =='expTypeNon'){
                let group = this.findCheckboxGroup()
                $(group.container).prepend(newMessage.message)
                group.messages.push(newMessage)
            }
        }
    }

    validateTextInput(){
        if(this.validate == true){
            let minCharCount = this.validate5CharMin()
            let nonBlankInput = this.validateTextPresent()
            if(minCharCount == true && nonBlankInput == true){
                this.isValidated = true
                this.removeMessages()
                return true
            }else{
                console.log('Input not valid!')
                if(nonBlankInput == false){
                    this.addRequiredMessage()
                }
                if(minCharCount == false){
                    this.addMin5CharMessage()
                }
                this.isValidated = false
                return false
            }
        }
        
    }

    validateCheckBox(){
        if(this.validate == true){
            this.isValidated = this.validateCheckBoxGroup()
            if (this.isValidated == false){
                this.addRequiredMessage()
                if( this.id == 'expTypeCan' || this.id == 'expTypeNon' ){FormButton.manageSubmitButtons()}
            }else if( this.isValidated == true){
                this.removeMessages()
            }
            
            return this.validateCheckBoxGroup()
        }
    }

    activeValidations(){
        
        if(this.type != 'checkbox'){
            $(this.input).on('input', ()=>{
                return this.validateTextInput()
            })
        }else if(this.type == 'checkbox'){
            $(this.input).on('change', ()=>{
                this.determineChecked()
                return this.validateCheckBox()
            })
        }
        
    }

    removeMessages(){
        if(this.type != 'checkbox'){
            $(this.messages).each((index, message)=>{
                message.removeMessage()
            })
            this.messages = []
        }else if(this.type == 'checkbox'){
            let group = this.findCheckboxGroup()
            $(group.messages).each((index, message)=>{
                console.log(`message to remove= ${message.id}`)
                message.removeMessage()
            })
            group.messages=[]
        }
    }

    validateThis(){
        if($(this.input).attr('data-validate') == 'false'){
            this.validate = false
        }else{
            this.validate = true
        }
    }
    
}

class CheckboxGroup{
    static allGroups = []

    constructor(parent, checkboxes){
        this.container=$(parent)
        this.parentId=$(parent).attr('id') // the id of the checkbox's parent div container identified by the name "checkbox-container" 
        this.checkboxes=checkboxes // list of the checkboxes that are for the same question
        this.required=$(parent).attr('data-required')
        this.messages=[]
        CheckboxGroup.allGroups.push(this)
    }

}

class FormButton{

    static allButtons = []
    static submitButtons = []
    static buttonButtons = []
    static resetButtons = []

    constructor(button){
        
            this.id = $(button).attr('id') || 'None'
            this.type = $(button).attr('type')
            this.button = button
            this.isActive = $(button).is(':disabled')
            this.isVisible = $(button).css('display') !== 'none'
    
            switch (this.type){
                case 'button':
                    FormButton.buttonButtons.push(this)
                    break
                case 'submit':
                    FormButton.submitButtons.push(this)
                    break
                case 'reset':
                    FormButton.resetButtons.push(this)
                    break
                    
            }
            FormButton.allButtons.push(this)
        
    }

    static init(formId){
        $(`#${formId}`).find('button').each((index, button)=>{
            const newFormButton = new FormButton(button)
        })
    }
    static getButtonById(id){
        let buttonToGet
        $(FormButton.allButtons).each((index, button)=>{
            if( button.id == id ){
                buttonToGet = button
            }
        })
        return buttonToGet
    }

    static manageSubmitButtons(canonical){
        let canButton = FormButton.getButtonById('canonicalSubmit')
        let nonCanButton = FormButton.getButtonById('nonCanonicalSubmit')
        let dependentQuestionIds = [
            'description',
            'hardware',
            'software',
            'leadExperimenterEmail',
        ]
        let formInputList = FormInput.getMultipleInputById(dependentQuestionIds)
        
        //canonical experiment
        if( canonical == true ){
            canButton.activateButton()
            nonCanButton.deactivateButton()
            $('p#type-message').hide()
            $(formInputList).each((index, input)=>{
                input.required = false
                input.validate = false
                $(input.input).removeAttr('required')
                $(input.input).attr({'data-validate': false})
                $("label[for='" + $(input.id) + "']").remove($('span[name=required-asterisk]'))
            })
        }
        //non canonical experiment
        else if( canonical == false ){
            nonCanButton.activateButton()
            canButton.deactivateButton()
            $('p#type-message').hide()
            $(formInputList).each((index, input)=>{
                input.required = true
                input.validate = true
                console.log(`${input.id} will now be validated: ${input.validate} `)
                console.log(`${input.id} is now required: ${input.required}`)
                $(input.input).prop('required',true)
                $(input.input).attr({'data-validate': true})
                $("label[for='" + $(input.id) + "']").append($('span[name=required-asterisk]'))
            })
        }
        //No experiment type selected
        else{
            $('p#type-message').show()
            nonCanButton.deactivateButton()
            canButton.deactivateButton()
        }

    }

    deactivateButton(){
        if( this.isActive ){
            $(this.button).addClass('disabled')
            this.isActive = false
        }else{console.log('button is already deactivated')}
    }
    
    activateButton(){
        if( !this.isActive ){
            $(this.button).removeClass('disabled')
            this.isActive = true
        }else{console.log('button is already activated')}
    }

    showButton(){
        $(this.button).show()
        this.isVisible = true
    }

    hideButton(){
        $(this.button).hide()
        this.isVisible = false        
    }

}

class FormValidation{

    constructor(form){
        this.form=form
        this.isValid=false
    }
    
    validateForm(){
        let validInputCount = 0
        $(FormInput.allFormInputs).each((inputIndex, input)=>{
            let isValid = true
            if(input.validate == true && $(input.input).attr('name') != 'csrfmiddlewaretoken'){
                if(input.type != 'checkbox'){
                    isValid = input.validateTextInput()
                }else if(input.type == 'checkbox'){
                    isValid = input.validateCheckBox()
                }
            }
            console.log(`${input.id} is ${isValid}`)
            if(isValid != true){validInputCount+=1}
        })

        if(validInputCount != 0){
            this.isValid = false
            return false                
        }else if(validInputCount == 0){
            this.isValid = true
            return true
        } 
    }

}


function studentExperiment(){
    $('#studentExperiment').on('click', ()=>{
        if( $('#studentExperiment').is(':checked') ){
            // Hide and mark the following fields
            // mark canonical
            $('#expTypeCan').prop('checked', true)
            $('#experimentTypeContainer').hide()
            // mark sponsored project - student project
            $('#sponsoredProject').val('N/A - Student Project')
            $('#experimentSponsoredProjectContainer').hide()
            // mark grant number - no
            $('#grantNumberNo').prop('checked', true)
            $('#experimentGrantNumberContainer').hide()
            // destination development
            $('#experimentLocation-Development').prop('checked', true)
            $('#experimentLocationContainer').hide()
            // urgency - no
            $('#urgentNo').prop('checked', true)
            $('#experimentUrgencyContainer').hide()
            // shared - no
            $('#shareNo').prop('checked', true)
            $('#experimentIsSharedContainer').hide()
            $('#hostInstitution').attr({'placeholder':'Enter the name of your college/university'})
            $('#leadExperimenterName').attr({'placeholder':'Enter your full name'})
            $('#leadExperimenterEmail').attr({'placeholder':'Enter your student email'})
            FormButton.manageSubmitButtons(true)
        }else{
            // Hide and mark the following fields
            // mark canonical
            $('#expTypeCan').prop('checked', false)
            $('#experimentTypeContainer').show()
            // mark sponsored project - student project
            $('#sponsoredProject').val('')
            $('#experimentSponsoredProjectContainer').show()
            // mark grant number - no
            $('#grantNumberNo').prop('checked', false)
            $('#experimentGrantNumberContainer').show()
            // destination development
            $('#experimentLocation-Development').prop('checked', false)
            $('#experimentLocationContainer').show()
            // urgency - no
            $('#urgentNo').prop('checked', false)
            $('#experimentUrgencyContainer').show()
            // shared - no
            $('#shareNo').prop('checked', false)
            $('#experimentIsSharedContainer').show()
            $('#create-experiment').find('p[name="studentMessage"]').each((i, message)=>{$(message).remove()})
            $('#hostInstitution').attr({'placeholder':''})
            $('#leadExperimenterName').attr({'placeholder':''})
            $('#leadExperimenterEmail').attr({'placeholder':''})
            FormButton.manageSubmitButtons()
        }
    })
}

FormInput.init($('#create-experiment'))
FormButton.init('create-experiment')

$(document).ready(()=>{
    // on every input change and checkbox check, validate the answer
    $(FormInput.allFormInputs).each((formInputIndex, formInput)=>{
        let validated = formInput.activeValidations()
        if(validated == true){
            formInput.removeMessages()
        }
    })
    $('form#create-experiment').on('submit', (e)=>{
    
            console.log('Form Submitted!')
            const newValidation = new FormValidation($('#create-experiment'))
            let isValid = newValidation.validateForm()
            if(isValid == false){
                e.preventDefault()
                $('div[name=create-exp-messages').append("<p class='text-danger'>Please fill in required fields and fix any errors before submitting</p>")
            }
        
    })
    studentExperiment()
})
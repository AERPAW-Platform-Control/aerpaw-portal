function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// setInterval variables: further defined in the functions below
let incompleteThreadInterval;
let errorInterval;


class AerpawThread{
    static completedThreads = []
    static incompleteThreads = []
    static allThreads = []

    constructor(id, message, isError, isComplete, isSuccess){
        this.id = id
        this.message = message
        this.isError = isError
        this.isComplete = isComplete
        this.isSuccess = isSuccess
        this.displayed = false
        this.setInterval = false
    }

    static findThreads(){
        fetch('http://127.0.0.1:8000/error_handling/ssh_error_handling',{
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken':getCookie('csrftoken')
            },
            body: JSON.stringify({'action':'threads_exist'}),
        })
        .then(response => response.json())
        .then(data => {
            let aerpawThreads = data['threads']
            if( aerpawThreads != 'NoneFound'){
                $(aerpawThreads).each((index, apThread) => {
                    $(Object.keys(apThread)).each((keyIndex, key) => {
                        let thread = apThread[key]
                        const newThread = new AerpawThread(thread['id'], thread['message'], thread['is_error'], thread['completed'], thread['is_success'])
                        newThread.updateThreadGroups()
                    })
                })
            }
            AerpawThread.updateMessageDisplay()
            if( AerpawThread.incompleteThreads.length > 0 ){
                let count = 0
                incompleteThreadInterval = setInterval(() => {
                    count += 1
                    AerpawThread.fetchIncompleteThreads()
                    if(AerpawThread.incompleteThreads.length === 0){
                        clearInterval(incompleteThreadInterval)
                    }
                }, 5000)
            }else{
                console.log('There are currently no incomplete threads')
            }
        })
    }

    static updateThreads(thread){
        let totalThreads = AerpawThread.allThreads.length
        let numberOfUnlikeThreads = 0
        AerpawThread.allThreads.forEach(aerpawThread => {
            if(aerpawThread.id == thread['id']){
                aerpawThread.message = thread['message']
                aerpawThread.isError = thread['is_error']
                aerpawThread.isComplete = thread['completed']
                return aerpawThread
            }else{
                numberOfUnlikeThreads += 1
            }
        })

        if( totalThreads == numberOfUnlikeThreads){
            const newThread = new AerpawThread(thread['id'], thread['message'], thread['is_error'],  thread['completed'], thread['is_success'])
            return newThread
        }
    }

    updateThreadGroups(){
        if(this.isComplete == false ){
            if( this.threadInGroup(AerpawThread.incompleteThreads) == false ){
                AerpawThread.incompleteThreads.push(this)
            }
            if( this.threadInGroup(AerpawThread.completedThreads) == true ){
                this.removeThreadFromGroup(AerpawThread.completedThreads)
            }
        }else if(this.isComplete == true ){
            if( this.threadInGroup(AerpawThread.incompleteThreads) == true ){
                this.removeThreadFromGroup(AerpawThread.incompleteThreads)
            }
            if( this.threadInGroup(AerpawThread.completedThreads) == false ){
                AerpawThread.completedThreads.push(this)
            }
        }else if(this.threadInGroup(AerpawThread.allThreads) == false){
            AerpawThread.allThreads.push(this)
        }
    }

    threadInGroup(threadGroup){
        let inGroup = false
        threadGroup.forEach(thread => {
            if(thread.id == this.id){
                inGroup = true
            }
        })
        return inGroup
    }

    removeThreadFromGroup(threadGroup){
        let indexToRemove = ''
        $(threadGroup).each((threadIndex, thread) => {
            if(thread.id == this.id){
                indexToRemove = threadIndex
            }
        })
        threadGroup.splice(indexToRemove, 1)
    }

    static fetchIncompleteThreads(){
        fetch('http://127.0.0.1:8000/error_handling/ssh_error_handling',{
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken':getCookie('csrftoken')
            },
            body: JSON.stringify({'action':'incomplete_threads'}),
        })
        .then(response => response.json())
        .then(data => {
            let aerpawThreads = data['threads']
            if( aerpawThreads == 'NoneFound'){
                console.log('No incomplete threads found')
            }else{
                $(aerpawThreads).each((index, apThread) => {
                    $(Object.keys(apThread)).each((keyIndex, key) => {
                        let thread = apThread[key]
                        thread = AerpawThread.updateThreads(thread)
                        thread.updateThreadGroups()
                    })
                })
                AerpawThread.updateMessageDisplay()
            }
        })
    
        
    }

    displayThreadMessage(){
        if(this.displayed == false){
            let fontColor = 'text-danger'
            if( this.isSuccess == true ){
                fontColor = 'text-success'
            }
            $('#aerpaw-messages').append(`<p id=${this.id} class=${fontColor}>${this.message}</p>`)
        }
    }

    static updateMessageDisplay(){
        var displayedThreads = []
        AerpawThread.completedThreads.forEach(thread => {
            if(thread.displayed == false && thread.isComplete == true){
                thread.displayThreadMessage()
                this.displayed = true
                displayedThreads.push(thread.id)
                thread.removeThreadFromGroup(AerpawThread.completedThreads)
            }
        })
        if(displayedThreads.length > 0 ){
            fetch('http://127.0.0.1:8000/error_handling/ssh_error_handling',{
                method: 'POST',
                headers: {
                    'Content-Type':'application/json',
                    'X-CSRFToken':getCookie('csrftoken')
                },
                body: JSON.stringify({'action':'mark_displayed', 'displayed_threads':displayedThreads}),
            })
            .then(response => response.json())
            .then(data => {
                console.log(`Is marking the threads as displayed a success? ${data['success']}`)
            })
        }
    }

}

class AerpawError{
    static allErrors = []
    static displayedErrors = []

    constructor(id, message, isDisplayed){
        this.id = id
        this.message = message
        this.isDisplayed = isDisplayed
    }

    static getErrors(){
        fetch('http://127.0.0.1:8000/error_handling/error_handling',{
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken':getCookie('csrftoken')
            },
            body: JSON.stringify({'action':'get_undisplayed_errors'})
        })
        .then(response => response.json())
        .then(data => {
            let errors = data['errors']
            $(errors).each((index, error)=>{
                let newError = new AerpawError(error['id'], error['message'], false)
                AerpawError.allErrors.push(newError)
            })
            AerpawError.displayErrorMessages()
        })
    }
    
    static displayErrorMessages(){
        $(AerpawError.allErrors).each((index, error)=>{
            if( error.isDisplayed == false){
                $('#aerpaw-messages').append(`<p id=${error.id} class='text-danger'>${error.message}</p>`)
                error.isDisplayed = true
                AerpawError.displayedErrors.push(error)
            }
        })
        AerpawError.markErrorsDisplayed()
    }

    static markErrorsDisplayed(){
        // create a list of the error ids of the errors that have been displayed
        // the Aerpaw.displayedErrors list is not json stringifiable becuase it is a list of objects
        let allErrors = AerpawError.displayedErrors
        let displayedErrorIds = []
        
        if(allErrors.length > 0){
            $(AerpawError.displayedErrors).each((index, error)=>{
                displayedErrorIds.push(error.id)
            })
            

            if(displayedErrorIds.length > 0){
                // send the displayed error ids to the backend
                fetch('http://127.0.0.1:8000/error_handling/error_handling',{
                    method: 'POST',
                    headers: {
                        'Content-Type':'application/json',
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        'action':'mark_errors_displayed',
                        'error_ids':displayedErrorIds
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(`Is marking the errors as displayed a success? ${data['success']}`)
                    
                    //Reset the displayedErrors list so that this function does not keep running
                    AerpawError.displayedErrors = []
                })
            }else{
                console.log(`There are no errors that are marked displayed`)
            }
        }else{
            console.log(`Woohoo! There are currently no errors!`)
        }
    }

    static startIntervalGetErrors(){
        let count = 0
        errorInterval = setInterval(() => {
            count += 1
            console.log(count)
            AerpawError.getErrors()
        }, 2000)
    }
}

AerpawThread.findThreads()
AerpawError.markErrorsDisplayed()
AerpawError.startIntervalGetErrors()
$(document).ready(()=>{
    $('button').each((btnIndex, btn) => {
        if($(btn).hasClass('thread')){
            $(btn).on('click', () => {
                setTimeout(AerpawThread.findThreads, 2000)
            })
        }
    })

})


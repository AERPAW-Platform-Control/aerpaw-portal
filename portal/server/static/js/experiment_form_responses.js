function clearExpFormDataModal(){
    $('p[name=expFormDataModal-p').each((pIndx, p) => {
        $(p).empty()
    })
}

function fillExpFormDataModal(data){
    Object.keys(data).forEach((key)=>{
        if(data[key] != ''){
            $(`#modal-${key}`).text(data[key])
        }else{
            $(`#modal-${key}`).text('None')

        }

    })
}


$('button[name=expFormDataModal-button]').each((btnIndx, btn) => {
    clearExpFormDataModal()

    $(btn).on('click', () => {
        let formDataId = $(btn).val()
        fetch('http://127.0.0.1:8000/operators/experiment-info/experiment_form_responses/',{
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken':getCookie('csrftoken')
            },
            body: JSON.stringify({'formDataId': `${formDataId}`}),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            fillExpFormDataModal(data)
        })
    })
})
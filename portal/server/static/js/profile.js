
$('#profile-roles-form').submit((e)=>{
    let btnClicked = document.activeElement
    $(btnClicked).addClass('disabled')
    if(confirm('By making this request you are verifying that you have read and accept all terms of the AERPAW Acceptable Use Policy')){
        console.log('confirmed')
    }else{
        console.log('canceled')
        e.preventDefault()
        $(btnClicked).removeClass('disabled')
    }

})
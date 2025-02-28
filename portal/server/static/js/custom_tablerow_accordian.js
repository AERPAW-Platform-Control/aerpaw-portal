/* 
The table row accordian needs a button named 'tr-accordian-button' with a data-target attr of'#id-of-tr'
the targeted tr needs to have an id to match the button data-target attr
*/

$('button[name=tr-accordian-button]').each((index,btn) =>{
    $(btn).on('click',()=>{
        let tableRowId = $(btn).attr('data-target')
        if($(btn).hasClass('collapsed-tr')){
            $(btn).removeClass('collapsed-tr')
            $(tableRowId).hide()
            
        }else{
            $(btn).addClass('collapsed-tr')
            $(tableRowId).show()
        }
    })
})
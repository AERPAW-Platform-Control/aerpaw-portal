class UserMessage{
    constructor(id, isRead, checkbox){
        this.id = id
        this.isRead = isRead
        this.checkbox = checkbox
    }

    static initUserMessages(){
        let table = document.getElementById('user-message-list-table')
        let rows = table.rows
        $(rows).each((rowIndex, row) => {
            if(rowIndex > 0){
                
                // create user message object
                let id = $(row).attr('data-message_id')
                let isRead = $(row).attr('data-isRead')
                let checkbox = $(row).find($('input[name=message-checkbox]'))
                const um = new UserMessage(id, isRead, checkbox)
                
                // add user message to correct groups
                um.manageMsgGroups()
            }
        });
    }
    
    static checkedMessage(){
        $(allMessages.messages).each((msgIndex, msg) => {
            $(msg.checkbox).on('click', ()=>{
                ActionButton.toggleOnOff()
                ActionButton.toggleDDCheckMark()
            })
        })
    }

    inGroup(group){
        let inGroup = group.messages.some(msg => msg.id === this.id)
        return inGroup
    }

    manageMsgGroups(){
        // add user message to correct groups
        if(this.inGroup(allMessages) == false){
            allMessages.messages.push(this)
        }
        if(this.isRead == 'True' && this.inGroup(readMessages) == false){
            readMessages.messages.push(this)
        }
        else if(this.isRead == 'False'){
            unreadMessages.messages.push(this)
        }
    }
}

class MessageGroup{
    constructor(groupAttr){
        this.attr = groupAttr
        this.messages = []
    }

    countCheckedMessages(){
        let count = 0
        $(this.messages).each((messageIndex, message) => {
            if($(message.checkbox).prop('checked') == true){
                count += 1
            }
        })
        return count
    }

    getCheckedMessages(){
        let checkedMsgs = []
        $(this.messages).each((index, msg)=>{
            if( $(msg.checkbox).prop('checked') == true ){
                checkedMsgs.push(msg)
            }
        })
        return checkedMsgs
    }

    getCheckedMessagesIds(checkedMessages=null){
        let checkedMsgIds = []
        if( checkedMessages == null ){
            // get checked messages if none are provided
            checkedMessages = this.getCheckedMessages()
        }
        $(checkedMessages).each((index, msg) => {
            checkedMsgIds.push(msg.id)
        })
        return checkedMsgIds
    }

    hasMsg(msg){
        let inGroup = this.messages.some(messageInGroup => messageInGroup.id === msg.id)
        return inGroup
    }

    removeMsg(msg){
        let inGroup = this.hasMsg(msg)
        console.log(`is message in ${this.attr} group? ${inGroup}`)
        console.log('removing message')
        let removeIndex
        this.messages.forEach((message, index)=>{
            if(message.id === msg.id){
                removeIndex = index
            }
        })
        this.messages.splice(removeIndex, 1)
        inGroup = this.hasMsg(msg)
        console.log(`is message in ${this.attr} group? ${inGroup}`)
    }

    addMsg(msg){
        console.log(`message is in ${this.attr} group? ${this.hasMsg(msg)}`)
        if(this.hasMsg(msg) == false){
            console.log(`adding message to group`)
            this.messages.push(msg)
        }
        console.log(`message is in ${this.attr} group? ${this.hasMsg(msg)}`)
    }

}

class ActionButton{
    constructor(id, isInactive, button){
        this.id = id
        this.isInactive = isInactive
        this.button = button
    }

    static toggleOnOff(){
        // check if any messages are selected
        if( allMessages.countCheckedMessages() > 0){
            deleteBtn.manageInactivity(false)
            
            // check if any read messages are selected
            if( readMessages.countCheckedMessages() > 0){
                markUnReadBtn.manageInactivity(false)
                
            }else{
                markUnReadBtn.manageInactivity(true)
                
            }

            // check if any unread messages are selected
            if( unreadMessages.countCheckedMessages() > 0){
                markReadBtn.manageInactivity(false)
            
            }else{
                markReadBtn.manageInactivity(true)
                
            }
        }else{
            deleteBtn.manageInactivity(true)
            markUnReadBtn.manageInactivity(true)
            markReadBtn.manageInactivity(true)
        }        
    }

    static buttonClick(){
        $('a[name="message-action-button"]').each((index, button) => {
            $(button).on('click', () => {
                let constBtn = 'None'
                $(allActionBtns).each((i, actionBtn) => {
                    if( $(button).attr('id') == actionBtn.id ){
                        constBtn = actionBtn
                    }
                })
                constBtn.manageMessageActions()
            })
        })
    }

    static toggleDDCheckMark(){
        console.log('toggle check mark')
        let emptyBox = $('#icon-none-selected')
        let minusBox = $('#icon-some-selected')
        let checkedBox = $('#icon-all-selected')
        let checkedMsgNum = allMessages.countCheckedMessages()
        let numOfMsgs = allMessages.messages.length
        console.log(`checkedMsgNum= ${checkedMsgNum}`)
        console.log(`numOfMsgs= ${numOfMsgs}`)
        if( checkedMsgNum == numOfMsgs){
            $(checkedBox).show()
            $(minusBox).hide()
            $(emptyBox).hide()
        }else if( checkedMsgNum > 0 && checkedMsgNum < numOfMsgs){
            $(checkedBox).hide()
            $(minusBox).show()
            $(emptyBox).hide()
        }else{
            $(checkedBox).hide()
            $(minusBox).hide()
            $(emptyBox).show()
        }
    }
    manageInactivity(isInactive){
        if(isInactive == false){
            if( $(this.button).hasClass('disabled') ){
                $(this.button).removeClass('disabled')
                this.isInactive = false
            }
        }else if(isInactive == true){
            if( !$(this.button).hasClass('disabled') ){
                $(this.button).addClass('disabled')
                this.isInactive = true
            }
        }
    }

    selectAllMessagesInGroup(group=null){
        if( group != null){
            $(allMessages.messages).each((messageIndex, message) => {
                let inGroup = group.messages.some(groupMessage => groupMessage.id === message.id)
                if( inGroup == true ){
                    $(message.checkbox).prop('checked', true)
                }else{
                    $(message.checkbox).prop('checked', false)
                }
            })
        }else{
            $(allMessages.messages).each((messageIndex, message) => {
                $(message.checkbox).prop('checked', false)
            })
        }
        ActionButton.toggleOnOff()
        ActionButton.toggleDDCheckMark()
    }

    deleteMessages(){

    }

    markUnread(){
    }

    markRead(){

    }

    manageMessageActions(){
        switch(this.id){
            case 'select-all-messages':
                this.selectAllMessagesInGroup(allMessages)
                break;
            case 'select-unread-messages':
                this.selectAllMessagesInGroup(unreadMessages)
                break;
            case 'select-read-messages':
                this.selectAllMessagesInGroup(readMessages)
                break;
            case 'select-none-messages':
                this.selectAllMessagesInGroup()
                break;
            case 'delete_user_message':
                this.deleteMessages()
                break;
            case 'mark_unread_user_message':
                this.markUnread()
                break;
            case 'mark_read_user_message':
                this.markRead()
                break;
            default:
                break;
        }
        ActionButton.toggleOnOff()
    }
}

// Create button and message group objects
const deleteBtn = new ActionButton('delete_user_message', $('#delete_user_message').hasClass('disabled'), $('#delete_user_message'))
const markUnReadBtn = new ActionButton('mark_unread_user_message', $('#mark_unread_user_message').hasClass('disabled'), $('#mark_unread_user_message'))
const markReadBtn = new ActionButton('mark_read_user_message', $('#mark_read_user_message').hasClass('disabled'), $('#mark_read_user_message'))
const selectAllBtn = new ActionButton('select-all-messages', $('#select-all-messages').hasClass('disabled'), $('#select-all-messages'))
const selectUnReadBtn = new ActionButton('select-unread-messages', $('#select-unread-messages').hasClass('disabled'), $('#select-unread-messages'))
const selectReadBtn = new ActionButton('select-read-messages', $('#select-read-messages').hasClass('disabled'), $('#select-read-messages'))
const selectNoneBtn = new ActionButton('select-none-messages', $('#select-none-messages').hasClass('disabled'), $('#select-none-messages'))
const allActionBtns = [deleteBtn, markUnReadBtn, markReadBtn, selectAllBtn, selectUnReadBtn, selectReadBtn, selectNoneBtn]
const readMessages = new MessageGroup('isRead')
const unreadMessages = new MessageGroup('isUnRead')
const allMessages = new MessageGroup('all')



$(document).ready(()=>{
    // Create message objects
    UserMessage.initUserMessages()

    UserMessage.checkedMessage()
    ActionButton.buttonClick()
})
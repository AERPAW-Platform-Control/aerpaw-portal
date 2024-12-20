

class ResourceGroup{
    

    constructor(id, isFixed, resources){
        this.id = id
        this.isFixed = isFixed || false
        this.resources = resources || []
        this.numberTargetedResources = 0
        this.availible = true
        this.location = ResourceGroup.location(this.id)
        ResourceGroup.allGroups.push(this)
    }

    getUnavailibleMessage(){
        let altLocation = null
        if( this.location == 'Centennial Campus'){
            altLocation = 'Lake Wheeler'
        } else if( this.location == 'Lake Wheeler' ){
            altLocation = 'Centennial Campus'
        }
        return `<li id="unavailibleMessage" class='list-group-item fs-6 text-danger'>
            <p>${this.location} resources are unavailible while ${altLocation} resources are selected.</p>
        </li>`
    }

    addResource(resource){
        this.resources.push(resource)
    }

    removeResource(resource){
        let resourceIndex = this.resources.findIndex(r => r === resource)
        if( resourceIndex != -1 ){
            this.resources.slice(resourceIndex, 1)
        }
    }

    markAvailible(){
        this.availible = true
        this.resources.forEach((resource) => {
            $(resource.element).prop('disabled', false)
            resource.unavailible = false
        })
        $('#unavailibleMessage').remove()
    }

    markUnAvailble(){
        this.availible = false
        this.resources.forEach((resource) => {
            $(resource.element).prop('checked', false)
            $(resource.element).prop('disabled', true)
            resource.targeted = false
            resource.unavailible = true
        })
        if( this.checkForMessage() == false ){
            $(this.id).find('ul').first().children('li').first().after(this.getUnavailibleMessage())
        }
    }

    countTargetedResources(){
        this.numberTargetedResources = 0
        this.resources.forEach((resource) => {
            if( resource.targeted == true){
                this.numberTargetedResources = this.numberTargetedResources += 1
            }
        })
        return this.numberTargetedResources
    }

    checkForMessage(){
        let hasMessage = false
        let message = $(this.id).find('#unavailibleMessage')
        if( message.length > 0){
            hasMessage = true
        }
        return hasMessage
    }

    static initAvailibility(){
        let numberCC = ccResources.countTargetedResources()
        let numberLW = lwResources.countTargetedResources()
        if( numberCC > 0 && numberLW == 0 ){
            lwResources.markUnAvailble()
        } else if ( numberCC == 0 && numberLW > 0 ){
            ccResources.markUnAvailble()
        }
    }

    static allGroups = []

    static location(id){
        let location = 'None'
        switch (id){
            case '#cc_resources':
                location = 'Centennial Campus'
                break
            case '#lw_resources':
                location = 'Lake Wheeler'
                break
            case '#pn_resources':
                location = 'Portable Nodes - No fixed Location'
                break
        }
        return location
    }

    static all(){
        return ResourceGroup.allGroups;
    }
}

class Resource{
    static allResources = []
    
    constructor(button){
        this.element = button
        this.id = $(button).attr('id')
        this.name = $(button).next('label').text()
        this.nodeNumber = 0
        this.location = $(button).data('location')
        this.targeted = $(button).prop('checked')
        this.unavailible = $(button).prop('disabled')
        this.nodeType = this.setNodeType(button)
        this.groupMember = []
        this.notGroupMember = []
        Resource.allResources.push(this)
    }

    get targetedResourceInputGroup(){
        return `<div class="row">
                    <div class="col-4">
                        <input name="node" class="form-control" type="text" value="${this.nodeNumber}" aria-label="Node Number"  readonly>
                    </div>
                    <div class="col-4">
                        <input class="form-control" type="text" value="${this.name}" aria-label="resource name"  readonly>
                    </div>
                    <div class="col-4 text-center">
                        <button id="down-${this.id}" name="nodeNumberBtn" type="button" class="btn btn-sm btn-outline-primary border border-0" onclick="changeNodeNumber(this)" data-ap-direction="down" data-ap-target="targetedResource-${this.id}">↑</button>
                        <button id="up-${this.id}" name="nodeNumberBtn" type="button" class="btn btn-sm btn-outline-primary border border-0" onclick="changeNodeNumber(this)" data-ap-direction="up" data-ap-target="targetedResource-${this.id}">↓</button>
                    </div>
                    <div class="col-4">
                        <input type="hidden" name="node_number" class="form-control" type="text" value="${this.id}-${this.nodeNumber}" aria-label="Node Number"  readonly>
                        <input type="hidden" name="resource_id" value="${this.id}">
                    </div>
                </div>`
    }

    get targetedResourceLi(){
        return `<li id="targetedResource-${this.id}" class="list-group-item" data-resource_id="${this.id}"></li>`
    }

    get targetedResourceListInputGroup(){
        return `<li id="targetedResource-${this.id}" class="list-group-item" data-resource_id="${this.id}">
                    <div class="row">
                        <div class="col-4">
                            <input name="node" class="form-control" type="text" value="${this.nodeNumber}" aria-label="Node Number"  readonly>
                        </div>
                        <div class="col-4">
                            <input class="form-control" type="text" value="${this.name}" aria-label="resource name" readonly>
                        </div>
                        <div class="col-4 text-center">
                            <button id="down-${this.id}" name="nodeNumberBtn" type="button" class="btn btn-sm btn-outline-primary border border-0" onclick="changeNodeNumber(this)" data-ap-direction="down" data-ap-target="targetedResource-${this.id}">↑</button>
                            <button id="up-${this.id}" name="nodeNumberBtn" type="button" class="btn btn-sm btn-outline-primary border border-0" onclick="changeNodeNumber(this)" data-ap-direction="up" data-ap-target="targetedResource-${this.id}">↓</button>
                        </div>
                        <div class="col-4">
                            <input type="hidden" name="node_number" class="form-control" type="text" value="${this.id}-${this.nodeNumber}" aria-label="Node Number"  readonly>
                            <input type="hidden" name="resource_id" value="${this.id}">
                        </div>
                    </div>
                </li>`
    }

    get getNodeNumber(){
        let nodeNumber = 0
        $('#exp_resources').find('li').each((i,li) => {
            if($(li).data('resource_id') == this.id){
                nodeNumber = i - 1
            }
        })
        return nodeNumber
    }

    static init(){
        $('input[name="resourceBtn"]').each((btnIndex, btn)=>{
            const resource = new Resource(btn)
        })
    }

    static all(){
        return Resource.allResources
    }
    
    static resetNodeNumbers(){
        $('#exp_resources').find('ul').children('li').each((i, li) => {
            allResources.resources.forEach((resource) => {
                if( $(li).data('resource_id') == resource.id ){
                    resource.nodeNumber = i - 1
                    $(li).empty()
                    $(li).append(resource.targetedResourceInputGroup)
                }

            })
        })
    }

    setNodeType(button){
        let nodeType = null
        let text = $(button).next('label').text()
        if( text.slice(0, 2) == 'CC' || text.slice(0, 2) == 'LW'){
            nodeType = 'fixed'
        }
        if( text.slice(0,3) == 'SPN' ){
            nodeType = 'smallPortable'
        }
        if( text.slice(0,3) == 'LPN' ){
            nodeType = 'largePortable'
        }
        return nodeType
    }

    countTargetedResourcesByNodeType(){
        let numberResources = 0
        Resource.all().forEach((resource) => {
            if(resource.targeted == true && resource.nodeType == this.nodeType){
                numberResources = numberResources += 1
            }
        })
        return numberResources
    }

    manageMessages(){
        let nodeTypeCount = this.countTargetedResourcesByNodeType()
        console.log(`this.nodeType: ${this.nodeType}`)
        switch(this.nodeType){
            case 'fixed':
                if( nodeTypeCount > 2){
                    fnTotalLimitMessage.appendMessage()
                }else{
                    fnTotalLimitMessage.removeMessage()
                }
                break
            case 'smallPortable':
                if( nodeTypeCount > 1){
                    smPNTotalLimitMessage.appendMessage()
                }else{
                    smPNTotalLimitMessage.removeMessage()
                }
                break
            case 'largePortable':
                if( nodeTypeCount > 1){
                    lgPNTotalLimitMessage.appendMessage()
                }else{
                    lgPNTotalLimitMessage.removeMessage()
                }
                break
        } 
    }

    markTargeted(){
        if( this.unavailible == false ){
            if( this.targeted == false ){
                this.targeted = true
                this.moveToTargetedList()
                expResources.addResource(this)
            }else{
                this.targeted =false
                this.removeFromTargetedList()
                expResources.removeResource(this)
            }
        } else {
            console.log('Resource is not availible to target')
            this.targeted = false
            this.removeFromTargetedList()
        }
        return this.targeted
    }

    updateMemberResourceGroups(){
        let memberOf = []
        ResourceGroup.allGroups.forEach((resourceGroup) => {
            if( resourceGroup.resources.includes(this) ){
                memberOf.push(resourceGroup)
            }
        })
        this.groupMember = memberOf
        return memberOf
    }

    notMemberResourceGroups(){
        let notMemberof = []
        ResourceGroup.allGroups.forEach((resourceGroup) => {
            if( !resourceGroup.resources.includes(this) ){
                notMemberof.push(resourceGroup)
            }
        })
        this.notGroupMember = notMemberof
        return notMemberof
    }

    setNodeNumber(){
        this.nodeNumber = this.getNodeNumber
        $('#exp_resources').find('ul').children('li').each((i, li) => {
            if( $(li).data("resource_id") == this.id ){
                $(li).empty()
                $(li).append(this.targetedResourceInputGroup)
            }
        })
    }

    inTargetedList(){
        let inList = false
        $('#exp_resources').find('li').each((i,li) => {
            if($(li).data('resource_id') == this.id ){
                inList = true
            }
        })
        return inList
    }

    moveToTargetedList(){
        if( this.inTargetedList() == false ){
            $('#exp_resources').find('ul').first().append(this.targetedResourceListInputGroup)
        }
        this.setNodeNumber()
        $('#exp_resources').find('button[name="nodeNumberBtn"]').each((i, button) => {
            NodeNumberButton.addNewNodeNumberButton(button)
        })
    }

    removeFromTargetedList(){
        $('#exp_resources').find('ul').children().each((i,li)=>{
            if($(li).data('resource_id') == this.id){
                $(li).remove()
            }
        })
        Resource.resetNodeNumbers()
        NodeNumberButton.all().forEach( (button) => {
            if(button.resourceId == this.id ){
                button.removeNodeButtonFromList()
            }
        })
    }
}

class NodeNumberButton{
    static allNodeButtons = []

    constructor(button){
        this.button = button
        this.id = $(button).attr('id')
        this.resourceId = $(button).data('ap-target').split('-')[1]
        this.direction = $(button).data('ap-direction')
        this.target = $(button).data('ap-target')
        NodeNumberButton.allNodeButtons.push(this)
    }

    get getResource(){
        let resourceMatch = 'None'
        allResources.resources.forEach((resource => {
            if(resource.id === this.resourceId){
                resourceMatch = resource
            }
        }))
        return resourceMatch
    }

    get targetIndex(){
        let targetIndex = null
        $('#exp_resources').find('li').each((i, li) => {
            if( li == document.getElementById(this.target)){
                targetIndex = i
            }
        })
        return targetIndex
    }

    static getNodeButton(buttonEl){
        let nodeButton = null
        NodeNumberButton.all().forEach( (button) => {
            if( $(button.button).attr('id') == $(buttonEl).attr('id') ){
                nodeButton = button
            }
        })
        return nodeButton
    }

    static inAllNodeButtonsList(button){
        let inList = false
        NodeNumberButton.all().forEach((btn) =>{
            if( btn.button === button ){
                inList = true
            }
        })
        return inList
    }

    static init(){
        $('button[name="nodeNumberBtn"]').each((i, button) => {
            const nodeButton = new NodeNumberButton(button)
        })
    }
    
    static addNewNodeNumberButton(button){
        let created = NodeNumberButton.inAllNodeButtonsList(button)
        if( created == false ){
            const nodeButton = new NodeNumberButton(button)
        }
    }

    static all(){
        return NodeNumberButton.allNodeButtons;
    }

    removeNodeButtonFromList(){
        let btnIndex = 'none'
        $(NodeNumberButton.all()).each((i,button) => {
            if( button == this){
                btnIndex = i
            }
        })
        if( btnIndex != 'none' ){
            NodeNumberButton.all().slice(btnIndex, 1)
        }
    }

    markNumberDown(){
        let currentIndex = this.targetIndex 
        let nextIndex = currentIndex - 1
        let targetedList =  $('#exp_resources').find('li')
        let targetLi = null
        if( nextIndex > 1 && nextIndex < targetedList.length){
            $(targetedList).each((i, li) => {
                if( i == currentIndex ){
                    targetLi = li
                    $(li).remove()
                }
            })
            $(targetedList).each((i, li) => {
                if( i == nextIndex ){
                    $(li).before(targetLi)
                }
            })
        }
        Resource.resetNodeNumbers()
    }

    markNumberUp(){
        let currentIndex = this.targetIndex 
        let nextIndex = currentIndex + 1
        let targetedList =  $('#exp_resources').find('li')
        let targetLi = null
        if( nextIndex > 0 && nextIndex < targetedList.length){
            $(targetedList).each((i, li) => {
                if( i == currentIndex ){
                    targetLi = li
                    $(li).remove()
                }
            })
            $(targetedList).each((i, li) => {
                if( i == nextIndex ){
                    $(li).after(targetLi)
                }
            })
        }
        Resource.resetNodeNumbers()
    }
}

class Messages{

    constructor(id, message){
        this.id = id
        this.messageContainer = $('#messageContainer')
        this.messageList = $('#messageList')
        this.message = message
    }

    static unavailible(resourceGroupLocation){
        let altLocation = null
        if( resourceGroupLocation == 'Centennial Campus'){
            altLocation = 'Lake Wheeler'
        } else if( resourceGroupLocation == 'Lake Wheeler' ){
            altLocation = 'Centennial Campus'
        }
        return `<li id="unavailibleMessage" class='list-group-item fs-6 text-danger'>
            <p>${resourceGroupLocation} resources are unavailible while ${altLocation} resources are selected.</p>
        </li>`
    }

    messageExists(messageId){
        let exists = false
        if( $(this.messageList).find(this.id).length > 0 ){
            exists = true
        }
        return exists
    }

    countMessages(){
        return this.messageList.find('li').length -1
        
    }

    appendMessage(){
        $(this.messageContainer).show()
        let exists = this.messageExists()
        if( exists == false ){
            this.messageList.append(this.message)
        }
    }

    removeMessage(){
        $(this.id).remove()
        if( this.countMessages() == 0 ){
            this.messageContainer.hide()
        }
    }
}

const ccResources = new ResourceGroup(id='#cc_resources', isFixed=true)
const lwResources = new ResourceGroup(id='#lw_resources', isFixed=true)
const pnResources = new ResourceGroup(id='#pn_resources')
const expResources = new ResourceGroup(id='#exp_resources')
const allResources = new ResourceGroup(id='#all_resources')
const fnLimitMessage = new Messages(id='#fixedNodeLmit', message= `<li id="fixedNodeLmit" class="list-group-item">
                                    <div>
                                        More than 2 fixed nodes selected
                                        <div class="ms-2 mt-1 text-secondary fs-6">
                                            **If you plan on using more than 2 fixed
                                            nodes, please refer to the <a href="">Aerpaw User manual</a>
                                            for more detailed information on the Sandbox Environment nodes. 
                                            If you are not planning on using the Sandbox Environment, please disregard 
                                            this message.
                                        </div>
                                    </div>
                                </li>` )
const smPNLimitMessage = new Messages(id='#smPortableNodeLimit', message=`<li id="smPortableNodeLimit" class="list-group-item fs-6">
                                        <div>
                                            More than 1 small portable node selected
                                            <div class="ms-2 text-secondary">
                                                **If you are planning on using more than 1 small portable 
                                                node, please refer to the <a href="">Aerpaw User manual</a>
                                                for more detailed information on the Sandbox Environment nodes. 
                                                If you are not planning on using the Sandbox Environment, please disregard 
                                                this message.
                                            </div>
                                        </div>
                                    </li>`)
const lgPNLimitMessage = new Messages(id='#lgPortableNodeLimit', message=`<li id="lgPortableNodeLimit" class="list-group-item fs-6">
                                        <div>
                                            More than 1 large portable node selected
                                            <div class="ms-2 text-secondary">
                                                **If you plan on using more than 1 large portable 
                                                node, please refer to the <a href="">Aerpaw User manual</a>
                                                for more detailed information on the Sandbox Environment nodes. 
                                                If you are not planning on using the Sandbox Environment, please disregard 
                                                this message.
                                            </div>
                                        </div>
                                    </li>`)
                                    
const fnTotalLimitMessage = new Messages(
    id='#fnTotalNodeLimit', 
    message=`<li id="fnTotalNodeLimit" class="list-group-item fs-6">
                <div>
                    Fixed Node Limit Reached for Sandbox Environment! 
                    <div class="ms-2 text-secondary">
                        **The Sandbox Environment is not setup to handle a total of more 
                        than 2 fixed nodes. It will be unavailible for this experiment 
                        unless 2 or fewer fixed nodes are selected.
                    </div>
                </div>
            </li>`)

const smPNTotalLimitMessage = new Messages(
    id='#smPNTotalNodeLimit', 
    message=`<li id="smPNTotalNodeLimit" class="list-group-item fs-6 ">
                <div>
                    Small Portable Node Limit Reached for Sandbox Environment! 
                    <div class="ms-2 text-secondary">
                        **The Sandbox Environment is not setup to handle a total of more 
                        than 1 small portable nodes. It will be unavailible for this 
                        experiment unless 1 or fewer small portable nodes are selected.
                    </div>
                </div>
            </li>`)

const lgPNTotalLimitMessage = new Messages(
    id='#lgPNTotalNodeLimit', 
    message=`<li id="lgPNTotalNodeLimit" class="list-group-item fs-6">
                <div>
                    Large Portable Node Limit Reached for Sandbox Environment! 
                    <div class="ms-2 text-secondary">
                        **The Sandbox Environment is not setup to handle a total of more 
                        than 1 large portable nodes. It will be unavailible for this 
                        experiment unless 1 or fewer large portable nodes are selected.
                    </div>
                </div>
            </li>`)

function initialNodeNumbers(){
    expResources.resources.forEach((resource) => {
        resource.setNodeNumber()
    })
}

function populateResourceGroups(resources){
    $(resources).each((resourceIndex, resource)=>{
       allResources.addResource(resource)
       if( resource.location == 'cc' ){
           ccResources.addResource(resource)
       } else if( resource.location == 'lw' ){
            lwResources.addResource(resource)  
       } else if( resource.location == 'pn'){
            pnResources.addResource(resource)
       }
       if( resource.targeted == true){
        expResources.resources.push(resource)
       }
    })
    initialNodeNumbers()

}

Resource.init()
NodeNumberButton.init()
populateResourceGroups(Resource.all())
ResourceGroup.initAvailibility()

Resource.all().forEach((resource)=>{
    
    resource.updateMemberResourceGroups()
    resource.notMemberResourceGroups()
    resource.manageMessages()

    $(resource.element).on('click', ()=> {
        resource.markTargeted()
        resource.manageMessages()
        if( resource.location == 'cc' || resource.location == 'lw' ){
            ResourceGroup.allGroups.forEach((resourceGroup) => {
                resourceGroup.countTargetedResources()
            })

            if( resource.targeted == true ){
                resource.notGroupMember.forEach((resourceGroup) => {
                    if( resourceGroup.isFixed == true ){
                        resourceGroup.markUnAvailble()
                    }
                })
            }else if ( resource.targeted == false ){
                let isNotMemberResourceGroupAvailible = false
                resource.groupMember.forEach((resourceGroup) => {
                    if( resourceGroup.numberTargetedResources == 0 ){
                        isNotMemberResourceGroupAvailible = true
                    }
                })
                if(isNotMemberResourceGroupAvailible == true){
                    resource.notGroupMember.forEach((resourceGroup) => {
                        if( resourceGroup.isFixed == true ){
                            resourceGroup.markAvailible()
                        }
                    })
                }
            }
        }
        
    })
})



function changeNodeNumber(button){
    let nodeBtn = NodeNumberButton.getNodeButton(button)
    if( nodeBtn.direction == 'down' ){
        nodeBtn.markNumberDown()
    } else if ( nodeBtn.direction == 'up' ){
        nodeBtn.markNumberUp()
    }
}
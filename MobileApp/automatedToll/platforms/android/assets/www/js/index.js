var app = {
    initialize: function() {
        this.bindEvents();
        $(window).on("navigate", function (event, data) {          
            event.preventDefault();      
        })
    },
    getStatusMessage:{
        "vehicleNumber":window.localStorage.getItem('number'),"requester":"APP","requestType":0
    },

    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
        app.pubnubInit()
    },
    
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
        if(window.localStorage.getItem('ui')) {
            window.localStorage.setItem('ui', 'REGISTER');
        }
    },
    receivedEvent: function(id) {
        var parentElement = document.getElementById(id);
        var listeningElement = parentElement.querySelector('.listening');
        var receivedElement = parentElement.querySelector('.received');
        listeningElement.setAttribute('style', 'display:none;');
        receivedElement.setAttribute('style', 'display:block;');
    },
    pubnubInit: function() {
        pubnub = PUBNUB({                          
            publish_key   : 'pub-c-913ab39c-d613-44b3-8622-2e56b8f5ea6d',
            subscribe_key : 'sub-c-8ad89b4e-a95e-11e5-a65d-02ee2ddab7fe'})
        app.render()
    },

    reset: function() {
        pubnub.unsubscribe({
            channel: window.localStorage.getItem('number'),
        });
        setTimeout(function(){
            localStorage.clear();
        },100);
        app.render()
    },
    
    addMoney: function(){
        var amt = document.getElementById("registerAmt").value;
        if(amt >= 100){
            document.getElementById('amtRe').innerHTML = "!!!HURRAY!!!<br>Your account has been recharged with &#8377;" + amt + "<br>··• )o( •··";    
            app.publish({"requester":"APP","requestType":1,"vehicleNumber":window.localStorage.getItem('number'),"rechargeAmt":amt})
        }
        else{
            document.getElementById('amtRe').innerHTML = "Minimun amount to recharge is &#8377; 100<br>*Please, enter the valid amount to recharge <br>··• )o( •··";
        }
    },

    transactionStart: function(){
        pubnub.subscribe({
            channel: window.localStorage.getItem('number')+window.localStorage.getItem('number'),
            message: function(m){
                $(document).ready(function(){
                    var tableNew = '<thead><tr><th><p>date/Time</p></th>' + 
                        '<th data-priority="1">Toll Name</th><th data-priority="2">Amt-Deducted' +
                        '</th><th data-priority="3">Amt-Added</th><th data-priority="3">Balance' +
                        '</th></tr></thead><tbody>'
                    for(var i = Object.keys(m).length - 1; i >= 0; i--){
                        tableNew += '<tr><th>'+ m[i][0] + '</th><td><b class="ui-table-cell-label">Toll Name</b>' + m[i][1] 
                        + '</td><td><b class="ui-table-cell-label">Amt-Deducted</b>' + m[i][2].toString() + '</td><td><b class="ui-table-cell-label">Amt-Added</b>' + 
                        m[i][3].toString() + '</td><td><b class="ui-table-cell-label">Balance</b>' + 
                        m[i][4].toString() + '</td></tr>';
                    };
                    tableNew += '</tbody>'
                    $('#transTable').html(tableNew);
                })
                },
                error: function (error) {
                  console.log(JSON.stringify(error));
                }
        })
        app.publish({"requester":"APP","requestType":2,"vehicleNumber":window.localStorage.getItem('number')});
    },

    /*SUBSCRIPTION TO VEHICLE CHANNEL*/
    subscribeStart: function(){         
        pubnub.subscribe({                                     
            channel : window.localStorage.getItem('number'),
            message : function(message){
                document.getElementById('userInfo').innerHTML = message.vehicleNumber;
                document.getElementById('userInfo1').innerHTML = message.ownerName;
                document.getElementById('userInfo2').innerHTML = message.vehicleType;
                document.getElementById('userInfo3').innerHTML = message.availableBal;
                if(message.warning != undefined || message.NHCrossed != undefined && message.dateTime != undefined && message.amtDeducted != undefined){
                    if(message.warning.length > 10 && message.NHCrossed != undefined){
                        alert(message.warning + "\nSpotted at " + message.NHCrossed) 
                    }
                    else if(message.warning.length > 10){
                        alert(message.warning)    
                    }
                    window.localStorage.setItem('localTollCross', message.NHCrossed)
                    window.localStorage.setItem('localDate', message.dateTime)
                    window.localStorage.setItem('localTime', message.dateTime1)
                    window.localStorage.setItem('localDeducted', message.amtDeducted)
                }
                document.getElementById('tollInfo').innerHTML = window.localStorage.getItem('localTollCross');
                document.getElementById('tollInfo1').innerHTML = window.localStorage.getItem('localDate');
                document.getElementById('tollInfo0').innerHTML = window.localStorage.getItem('localTime');
                document.getElementById('tollInfo2').innerHTML = window.localStorage.getItem('localDeducted');
            },            
            connect: function(){
                app.publish(app.getStatusMessage);
            }
        })
    },

    /* REGISTERING THE CAR NUMBER TO THE CHANNEL AND ADDING TO LOCAL STORAGE */ 

    register: function() {
        $(document).ready(function(){       
            $(':mobile-pagecontainer').pagecontainer('change', $('#appRegister'));        
            $('#vehicle-num-submit').click(function(){
                if ($('#numberVehicle').val() != '') {
                    window.localStorage.setItem('ui', 'DEFAULT')
                    window.localStorage.setItem('number', $('#numberVehicle').val())
                    app.render()    
                    window.location.replace('index.html');
                }
            })
        })
    },

    default: function() {
        app.subscribeStart();
        $(document).ready(function(){
            $(':mobile-pagecontainer').pagecontainer('change', $('#vehicleInfo'));
            $('#amountButton').on('click', function () {
                setTimeout(function () {
                    $('#addamtpop').popup('open', {
                    transition: 'pop'
                    });
                }, 1000);
            });
            $('#transactionButton').on('click', function () {
                setTimeout(function () {
                    $('#transaction').popup('open', {
                    transition: 'pop'
                    });
                }, 1000);
            });
        });
    },

    render: function() {
        if(!window.localStorage.getItem('ui')) {
            window.localStorage.setItem('ui', 'REGISTER');
        }
        switch(window.localStorage.getItem('ui')) {
            case 'REGISTER':
                app.register();
                break;
            default: 
                app.default();
        }
    },

    showLoading: function(text) {
        $.mobile.loading("show");
    },

    publish: function(message) {
        pubnub.publish({                                    
            channel : "vehicleIdentificanApp-req",
            message : message,
            callback: function(m){ console.log(m) }
        })
    }
};
app.initialize();

//End of the Program
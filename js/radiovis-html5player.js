window.onload = function(){	
}

function fadeOut(el, tout = 1000){
	document.querySelector(":root").style.setProperty("--fade-out", tout);
	el.classList.remove("fadeIn");
	el.classList.add("fadeOut");
	setTimeout(function(){
		if(el.classList.contains("fadeOut"))
			el.classList.add("hidden");
	}, tout);
}

function fadeIn(el, tout = 1000){
	document.querySelector(":root").style.setProperty("--fade-in", tout);
	el.classList.remove("hidden");
	el.classList.remove("fadeOut");
	el.classList.add("fadeIn");
}

class Frame extends HTMLElement
{
	constructor(){
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = `
		<link rel='stylesheet' type='text/css' href='css/style.css'/>
		<div class="radiovis-mainframe">
		    <div class="radiovis-slideframe"
		        <div class="radiovis-P1"><a href="" class="radiovis-LI"><img class="radiovis-I1" src="images/first_image.png"></a></div>
		        <div class="radiovis-P0"><a href="" class="radiovis-LI"><img class="radiovis-I0" src="images/first_image.png"></a></div>
		    </div>
		</div>
		<div class="radiovis-outtertext"><div class='radiovis-innertext'>Initialization...</div></div>
		`
		
		this.host = undefined;
		this.port = undefined;
		this.ws = undefined;
		this.NoFQDNFound = false;
	}
	
	connectedCallback() {
		if(this.host == undefined) {
			this.host = window.location.hostname;
		}
		console.log(this.port);
		if(!this.port){
			this.port = 8777;
		}
		
		this.classList.add("radiovis-main");
		this.initVisSocket(this);
	}
	
	disconnectedCallback() {
		
	}
	
	static get observedAttributes() { return ["topic", "host", "port" ]; }
	
	attributeChangedCallback(name, oldValue, newValue){
		console.log(name + " changed from " + oldValue + " to " + newValue); 
		switch(name){
			case "topic":
			this.topic = newValue;
			break;
			case "host":
			this.host = newValue;
			break;
			case "port":
			this.port = newValue;
			break;
		}
	}
	
	get topic() {
		return this._topic;
	}
	
	set topic(newValue) {
		this._topic = newValue;
	}
	
	get host() {
		return this._host;
	}
	
	set host(newValue){
		this._host = newValue;
	}
	
	get port() {
		return this._port;
	}
	
	set port(newValue){
		console.log("PORT");
		if(typeof newValue === "number")
			this._port = newValue;
		else
			this._port = Number(newValue);
		console.log("PORT END");
	}
	
	
	initVisSocket(el) {
		console.log(el);
		console.log("TOPIC: " + el.topic);
		console.log("HOST: " + el.host);
		console.log("PORT: " + el.port);
	
		var ws = new WebSocket("ws://" + el.host + ":" + el.port + el.topic);
		el.shadowRoot.querySelector('.radiovis-innertext').innerHTML = "Connecting to " + el.topic + "...";
		
		var radiovisplayer_connected_message = 'Connected, waiting for the first message !';
	
		ws.onconnect = function (evt)
		{
			
		}
	
		ws.onmessage = function (evt) 
		{ 
			var message = evt.data;
			var splited_message = message.split(':');
	
			if (splited_message[0] == 'RADIOVISWEBSOCKET') {  // Internal message
				if (splited_message[1] == 'HELLO\x00') {
					el.shadowRoot.querySelector(".radiovis-innertext").innerHTML = radiovisplayer_connected_message;
					return;
				}
				if (splited_message[1] == 'ERROR') {
					el.shadowRoot.querySelector(".radiovis-innertext").innerHTML = '<span style="color: red;">Error: ' + splited_message[2] + '</span>';
					return;
				}
				el.shadowRoot.querySelector(".radiovis-innertext").innerHTML = '<span style="color: red;">Unexpected reply: ' + splited_message[1] + '</span>';
				el.NoFQDNFound = true;
			} else {
				let command = '';
				let headers = new Array();
				let body = '';
				let headerMode = true;
				let start = 1;
				let data = evt.data.split('\n');
				let lastShow = '';
				let toShow = 0;
				
				if (data[0] != '') {
					command = data[0];
					start = 1;
				} else {
					command = data[1];
					start = 2;
				}
	
				for(var i = start; i < data.length; i++) {
					if (data[i] == '' && headerMode) {  // Switch from headers to body
						headerMode = false;
					} else if (headerMode) {  // Add header to the list
						let sdata = data[i].split(':', 1);
						headers[sdata[0]] = data[i].substr(sdata[0].length+1);
					} else {  // Compute the body
						body += data[i] + '\n';
					}
				}
	
				// Remove the last \n
				body = body.substr(0, body.length-1);
	
				//Is it a message ?
				if (command == 'MESSAGE') {
	
					//Is it for text ?
					if (headers['destination']  == el.topic + '/text') {
						//Do we have to show text ?
						if (body.substr(0, 5) == 'TEXT ') {	
							el.shadowRoot.querySelector('.radiovis-innertext').innerHTML = body.substr(5);
						}
					}
	
					//Is it for images ?
					if (headers['destination']  == el.topic + '/image') {
						//Do we have to show an image ?
						if (body.substr(0, 5) == 'SHOW ') {
	
							//FInd the image to use						
							if (el.hasAttribute('lastImageShown'))
								lastShow = el.getAttribute('lastImageShown');
							else 
								lastShow = '1';
	
							toShow = 1 - lastShow;
	
							//Set the src
							el.shadowRoot.querySelector('.radiovis-I' + toShow).setAttribute('src', body.substr(5));
	
							//Nice effect
							if(toShow == 1) {
								fadeOut(el.shadowRoot.querySelector('.radiovis-I0'));
								fadeIn(el.shadowRoot.querySelector('.radiovis-I1'));
							}
							else {
								fadeOut(el.shadowRoot.querySelector('.radiovis-I1'));
								fadeIn(el.shadowRoot.querySelector('.radiovis-I0'));
							}
	
							el.setAttribute('lastImageShown', toShow);
	
							//Some radio dosen't send text. If we're still on the default message, remove it
							if (el.shadowRoot.querySelector('.radiovis-innertext').innerHTML == radiovisplayer_connected_message)
								el.shadowRoot.querySelector('.radiovis-innertext').innerHTML = "";
	
							//Update link
							if (headers['link'])
								el.shadowRoot.querySelector('a').setAttribute('href', headers['link']);
							else
								el.shadowRoot.querySelector('a').setAttribute('href', '#');
						}
					}
				}
			}
		};
		
		ws.onclose = function(evt)
		{ 
			console.log(el);
			console.log(el.topic + " Connection lost");
			setTimeout(function(){
				if(!el.NoFQDNFound)
					el.initVisSocket(el);
			}, 1000);
			
		};
	}
}

customElements.define("custom-frame", Frame);

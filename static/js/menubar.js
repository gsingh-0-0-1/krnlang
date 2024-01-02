function requestTemplateEl(name) {
	var req = new XMLHttpRequest;
	req.open("GET", "/static/" + name + ".html")
	req.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var el = document.createElement('div')
			el.innerHTML = this.responseText
			document.body.appendChild(el)
		}
	}
	req.send()
}

requestTemplateEl("menubar")
requestTemplateEl("credits")
$(document).ready(function() {
	// Autosize for add tray
	autosize($("#add-tray textarea"));


	// Add tray
	// --------------------------------------------------
	
	$("#add-tray a#save-button").on("click", _submitAddTray);


	// Header controls
	// --------------------------------------------------

	$("header .controls a.add-button").on("click", _toggleAddTray);
	$("header .controls a.search-button").on("click", _toggleSearchTray);


	// Keyboard shortcuts
	// --------------------------------------------------

	// Search tray
	Mousetrap.bind('/', _showSearchTray);

	var field = document.querySelector('#search-tray input[type=text]');
	Mousetrap(field).bind('esc', _hideSearchTray);

	// Add tray
	Mousetrap.bind('a', _showAddTray);

	var field = document.querySelector('#add-tray textarea');
	Mousetrap(field).bind('esc', _hideAddTray);
	Mousetrap(field).bind(['mod+enter', 'shift+enter'], _submitAddTray);

	// Home
	Mousetrap.bind('g h', function() {
		window.location.href = config.url;

		return false;
	});
});


// Search tray
// --------------------------------------------------

function _showSearchTray() {
	// Display and focus on the search tray
	$("#search-tray input[type=text]").val('');

	$("#search-tray").slideDown(75, function() {
		$("#search-tray input[type=text]").focus();
	});

	return false;
}

function _hideSearchTray() {
	// Hide the search tray
	$("#search-tray").slideUp(75, function() {
		$("#search-tray input").val('').blur();
	});

	return false;
}

function _toggleSearchTray() {
	if ($("#search-tray:visible").length > 0) {
		_hideSearchTray();
	} else {
		_showSearchTray();
	}

	return false;
}


// Add tray
// --------------------------------------------------

function _showAddTray() {
	// Display and focus on the add tray
	$("#add-tray textarea").val('');

	$("#add-tray").slideDown(75, function() {
		$("#add-tray textarea").focus();
	});

	return false;
}

function _hideAddTray() {
	// Hide the add tray
	$("#add-tray").slideUp(75, function() {
		$("#add-tray textarea").val('').blur();
	});

	return false;
}

function _toggleAddTray() {
	if ($("#add-tray:visible").length > 0) {
		_hideAddTray();
	} else {
		_showAddTray();
	}

	return false;
}

function _submitAddTray() {
	// Get value of textarea
	var text = $("#add-tray textarea").val().trim();

	// Make sure it's not blank
	if (text == '') return;

	// URL/key for web service
	var url = $("#add-tray").attr("data-uri");
	var key = config.apiKey; // TODO: this is horrible, fix it soon

	// Payload
	var data = {
		'payload': text,
		'key': key,
	};

	// Check if we should pass in context/list
	var contextSlug = $("#page-data").attr("data-context-slug");
	var listSlug = $("#page-data").attr("data-list-slug");
	var parentListSlug = $("#page-data").attr("data-parent-list-slug");

	if (contextSlug != '') data['context'] = contextSlug;
	if (listSlug != '') data['list'] = listSlug;
	if (parentListSlug != '') data['parent_list'] = parentListSlug;

	$.ajax({
		url: url,
		method: 'POST',
		data: data,
		success: function(data) {
			// Hide the tray
			_hideAddTray();

			// Reload the page
			window.location.reload();
		},
		error: function(data) {
			console.log("error :(", data);
		},
	});

	return false;
}


// CSRF stuff

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

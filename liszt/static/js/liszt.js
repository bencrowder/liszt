$(document).ready(function() {
	// Autosize for add tray
	autosize($("#add-tray textarea"));


	// Add tray
	// --------------------------------------------------

	$("#add-tray a#save-button").on("click", _submitAddTray);


	// Search tray
	// --------------------------------------------------

	$("#search-tray input[type=text]").on("keyup", _submitSearchTray);


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


	// Item toggles
	// --------------------------------------------------

	$("#content").on("click", "ul.items li.item input", function() {
		var url = $(this).parents("li.item").attr("data-item-uri");

		var data = {
			'key': config.apiKey,
		};

		$.ajax({
			url: url,
			method: 'GET',
			data: data,
			success: function(data) {
			},
			error: function(data) {
				console.log("error :(", data);
				return false;
			},
		});
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
		$("#content .results").hide().siblings(".wrapper").show();
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

function _submitSearchTray() {
	// Get value of text box
	var query = $("#search-tray input[type=text]").val().trim();

	// URL for web service
	var url = $("#search-tray").attr("data-uri");

	// Make sure it's not blank
	if (query == '') {
		$("#content .results").hide().html('').siblings(".wrapper").show();
	} else {
		// Payload
		var data = {
			'q': query,
		};

		$.ajax({
			url: url,
			method: 'GET',
			data: data,
			success: function(data) {
				// Update the search results
				var html = '';

				// Total
				var totalResults = data.contexts.length + data.lists.length + data.items.length;
				html += '<h2>' + totalResults + ' result' + (totalResults != 1 ? 's' : '') + '</h2>';

				// Contexts
				if (data.contexts.length > 0) {
					html += '<ul class="contexts lists">';
					for (var i=0; i<data.contexts.length; i++) {
						var c = data.contexts[i];
						html += '<li class="list">';
						html += '<a href="' + c.url + '">' + c.name + '</a> <span>' + c.num_lists + ' lists</span>';
						html += '</li>';
					}
					html += '</ul>';
				}

				// Lists
				if (data.lists.length > 0) {
					html += '<ul class="lists">';
					for (var i=0; i<data.lists.length; i++) {
						var l = data.lists[i];
						html += '<li class="list">';
						html += '<a href="' + l.url + '">' + l.name + '</a> <span>' + l.num_items + ' items';
						if (l.num_lists > 0) {
							html += ', ' + l.num_lists + ' lists';
						}
						html += '</span>';
						html += '</li>';
					}
					html += '</ul>';
				}

				// Items
				if (data.items.length > 0) {
					html += '<ul class="items">';
					for (var i=0; i<data.items.length; i++) {
						var item = data.items[i];
						html += '<li class="item" data-toggle-item-uri="' + item.toggle_uri + '">';
						html += '<input type="checkbox"';
						if (item.checked) {
							html += ' checked="' + item.checked + '"';
						}
						html += '/> ';
						html += '<label>' + item.name + '</label>';
						html += '</li>';
					}
					html += '</ul>';
				}

				// Put the HTML in the results panel
				$("#content .results").html(html);

				// Show the results panel if it's not visible
				if ($("#content .results:visible").length == 0) {
					$("#content .results").show().siblings(".wrapper").hide();
				}
			},
			error: function(data) {
				console.log("error :(", data);
			},
		});
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
// --------------------------------------------------

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

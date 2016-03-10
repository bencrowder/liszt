$(document).ready(function() {
	// Menu code
	// --------------------------------------------------

	function _toggleMenu() {
		$("body").toggleClass("active-nav");
	}

	function _showMenu() {
		$("body").addClass("active-nav");
	}

	function _hideMenu() {
		$("body").removeClass("active-nav");
	}

	$("a.menu").on("click touchstart", function() {
		_toggleMenu();
		return false;
	});

	$(".mask").on("click touchstart", function(e) {
		_hideMenu();
		return false;
	});

	Mousetrap.bind('g m', _toggleMenu);


	// Add tray
	// --------------------------------------------------

	// Autosize for add tray
	autosize($("#add-tray textarea"));

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
	Mousetrap(field).bind('enter', _followSearch);

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

	// Starred
	Mousetrap.bind('g s', function() {
		window.location.href = config.url + "starred/";

		return false;
	});

	// Up a level
	Mousetrap.bind('g u', function() {
		parentUri = $("body").data("parent-uri");

		if (parentUri != '') {
			window.location.href = parentUri;
		}

		return false;
	});

	// Dark mode
	Mousetrap.bind('g d', function() {
		$("body").toggleClass("dark");

		return false;
	});

	$("a#toggle-dark-mode").on("click", function() {
		$("body").toggleClass("dark");
		_toggleMenu();

		return false;
	});

	// Overview
	Mousetrap.bind('g o', function() {
		window.location.href = $("nav[role=menu] .overview-link").attr("href");
	});


	// Item toggles
	// --------------------------------------------------

	// Checkbox
	$("#content").on("tap", "ul.items li.item input[type=checkbox]", function() {
		var url = $(this).parents("li.item").attr("data-item-uri");

		var data = {
			'key': config.apiKey,
		};

		var item = $(this);

		$.ajax({
			url: url,
			method: 'GET',
			data: data,
			success: function(data) {
				item.prop("checked", !item.prop("checked"));
				return false;
			},
			error: function(data) {
				console.log("error :(", data);
				return false;
			},
		});

		return false;
	});

	// Starring
	$("#content").on("doubletap", "li.item .wrapper > label", function() {
		var url = $(this).closest("li.item").attr("data-star-item-uri");
		var star = $(this).closest(".wrapper").siblings(".star");

		var data = {
			'key': config.apiKey,
		};

		$.ajax({
			url: url,
			method: 'GET',
			data: data,
			success: function(data) {
				star.toggleClass("hide");
			},
			error: function(data) {
				console.log("error :(", data);
				return false;
			},
		});

		return false;
	});


	// Sorting items in a list
	// --------------------------------------------------

	var itemLists = $("ul.items.sortable");
	for (var i=0; i<itemLists.length; i++) {
		var itemList = itemLists[i];
		var sortable = new Sortable(itemList, {
			draggable: "li.item",
			handle: ".handle",
			ghostClass: "placeholder",
			onUpdate: function(e) {
				var item = $(e.item);
				var order = [];
				var items = item.parents("ul.items").find("li.item");

				for (var i=0; i<items.length; i++) {
					var item = $(items[i]);
					order.push(parseInt(item.attr("data-item-id")));
				}

				var url = item.parents("ul.items").attr("data-sort-uri");

				var data = {
					ids: order.join(','),
					key: config.apiKey,
				};

				$.ajax({
					url: url,
					method: 'POST',
					data: data,
					success: function(data) {
					},
					error: function(data) {
						console.log("Error! :(", data);
					},
				});
			},
		});
	}


	// Sorting lists in a context
	// --------------------------------------------------

	var listLists = $("ul.lists");
	for (var i=0; i<listLists.length; i++) {
		var listList = listLists[i];
		var sortable = new Sortable(listList, {
			draggable: "li.list",
			handle: ".handle",
			ghostClass: "placeholder",
			onUpdate: function(e) {
				var item = $(e.item);
				var order = [];
				var items = item.parents("ul.lists").find("li.list");

				for (var i=0; i<items.length; i++) {
					var item = $(items[i]);
					order.push(parseInt(item.attr("data-object-id")));
				}

				var url = item.parents("ul.lists").attr("data-sort-uri");

				var data = {
					ids: order.join(','),
					key: config.apiKey,
				};

				$.ajax({
					url: url,
					method: 'POST',
					data: data,
					success: function(data) {
					},
					error: function(data) {
						console.log("Error! :(", data);
					},
				});
			},
		});
	}


	// Item editing
	// --------------------------------------------------

	$("#content").on("doubletap", "li.item .handle", function() {
		var controls = $(this).siblings(".wrapper").find(".edit-controls");
		var labels = $(this).siblings(".wrapper").find("> label, > .subtitle");

		labels.fadeOut(75, function() {
			controls.fadeIn(75, function () {
				autosize(controls.find("textarea"));
				controls.find("textarea.item-text").focus();
			});
		});

		return false;
	});

	function _hideEditControls(item, fast) {
		var controls = item.parents(".edit-controls");
		var labels = controls.siblings("label, .subtitle");

		if (fast) {
			controls.hide();
			labels.show();
		} else {
			controls.fadeOut(75, function() {
				labels.fadeIn(75);
			});
		}
	}

	$("#content").on("tap", "li.item .wrapper .edit-controls .cancel", function() {
		_hideEditControls($(this), true);

		return false;
	});

	$("#content").on("tap", "li.item .wrapper .edit-controls .star", function() {
		$(this).toggleClass("selected");

		return false;
	});

	var fields = document.querySelectorAll('.edit-controls textarea');
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('esc', function(e) {
			_hideEditControls($(e.target))
		});

		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter', 'enter'], function(e) {
			_saveItem($(e.target))

			return false;
		});
	}

	// Save
	function _saveItem(item) {
		var controls = item.parents(".edit-controls");

		var url = controls.attr("data-update-uri");

		var label = controls.siblings("label");
		var notes = label.siblings(".subtitle.notes");

		var newText = controls.find("textarea.item-text").val().trim();
		var metadata = controls.find("textarea.item-metadata").val().trim();

		var starred = controls.find(".star").hasClass("selected");
		if (starred) {
			newText += " *";
		}

		var selector = metadata.split("\n")[0];
		var itemId = metadata.split("\n")[1].slice(4).trim();

		var data = {
			'key': config.apiKey,
			'text': newText,
			'selector': selector,
			'id': itemId,
		};

		$.ajax({
			url: url,
			method: 'POST',
			data: data,
			success: function(data) {
				// Update the label/subtitle
				label.html(data.item.text);

				if (data.item.notes) {
					if (notes.length > 0) {
						notes.html(data.item.notes);
					} else {
						// Create the notes part
						$("<span class='subtitle notes'>" + data.item.notes + "</span>").insertAfter(label);
					}
				} else {
					// Remove it if it's there
					if (notes.length > 0) {
						notes.slideUp(200).remove();
					}
				}

				// Update star
				var star = controls.closest(".wrapper").siblings(".star");
				if (data.item.starred) {
					star.removeClass("hide");
				} else {
					star.addClass("hide");
				}

				_hideEditControls(item);
			},
			error: function(data) {
				console.log("error :(", data);
			},
		});

		return false;
	}

	$("#content").on("tap", "li.item .wrapper .edit-controls .save", function() {
		_saveItem($(this));

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

function _followSearch() {
	// Go to the first thing listed
	if ($("#content .results ul.objects").length > 0) {
		var url = $("#content .results ul.objects:first li:first .wrapper > a").attr("href");

		window.location.href = url;
	}
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

				if (data.contexts && data.lists && data.items) {
					// Total
					var totalResults = data.contexts.length + data.lists.length + data.items.length;
					html += '<h2>' + totalResults + ' result' + (totalResults != 1 ? 's' : '') + '</h2>';

					// Contexts
					if (data.contexts.length > 0) {
						html += '<ul class="contexts lists objects">';
						for (var i=0; i<data.contexts.length; i++) {
							var c = data.contexts[i];
							html += '<li class="list">';
							html += '<div class="wrapper">';
							html += '<a href="' + c.url + '">' + c.slug + '</a> ';
							html += '<span class="subtitle">' + c.num_lists + ' list';
							if (c.num_lists != 1) html += 's';
							html += '</span>';
							html += '</div>';
							html += '</li>';
						}
						html += '</ul>';
					}

					// Lists
					if (data.lists.length > 0) {
						html += '<ul class="lists objects">';
						for (var i=0; i<data.lists.length; i++) {
							var l = data.lists[i];
							html += '<li class="list">';
							html += '<div class="wrapper">';
							html += '<a href="' + l.url + '">' + l.slug + '</a> ';
							html += '<span class="subtitle">' + l.num_items + ' item';
							if (l.num_items != 1) html += 's';
							if (l.num_lists > 0) {
								html += ', ' + l.num_lists + ' list';
								if (l.num_lists != 1) html += 's';
							}
							html += ', <a class="context" href="' + l.context_url + '">' + l.context_slug + '</a>';
							if (l.parent_list_slug) {
								html += '&thinsp;<a class="list" href="' + l.parent_list_url + '">' + l.parent_list_slug + '</a></span>';
							}
							html += '</span>';
							html += '</div>';
							html += '</li>';
						}
						html += '</ul>';
					}

					// Items
					if (data.items.length > 0) {
						html += '<ul class="items objects">';
						for (var i=0; i<data.items.length; i++) {
							html += data.items[i].html;
						}
						html += '</ul>';
					}
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

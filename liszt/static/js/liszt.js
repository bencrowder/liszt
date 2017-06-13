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
	Mousetrap.bind('g -', function() {
		window.location.href = config.url;

		return false;
	});

	// Starred
	Mousetrap.bind('g .', function() {
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

	// Contextview
	Mousetrap.bind('g v', function() {
		window.location.href = $("nav[role=menu] .contextview-link").attr("href");
	});

	// Overview
	Mousetrap.bind('g o', function() {
		window.location.href = $("nav[role=menu] .overview-link").attr("href");
	});

	// Review
	Mousetrap.bind('g r', function() {
		window.location.href = $("nav[role=menu] .review-link").attr("href");
	});

	// Contextviews
	// TODO: make this suck less
	Mousetrap.bind('g 1', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(1) a.cv").attr("href");
	});

	Mousetrap.bind('g 2', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(2) a.cv").attr("href");
	});

	Mousetrap.bind('g 3', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(3) a.cv").attr("href");
	});

	Mousetrap.bind('g 4', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(4) a.cv").attr("href");
	});

	Mousetrap.bind('g 5', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(5) a.cv").attr("href");
	});

	Mousetrap.bind('g 6', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(6) a.cv").attr("href");
	});

	Mousetrap.bind('g 7', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(7) a.cv").attr("href");
	});

	Mousetrap.bind('g 8', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(8) a.cv").attr("href");
	});

	Mousetrap.bind('g 9', function() {
		window.location.href = $("nav[role=menu] .context:nth-child(9) a.cv").attr("href");
	});

	Mousetrap.bind('g h', function() {
		window.location.href = $("nav[role=menu] a.cv[data-slug=home]").attr("href");
	});

	Mousetrap.bind('g p', function() {
		window.location.href = $("nav[role=menu] a.cv[data-slug=projects]").attr("href");
	});

	Mousetrap.bind('g s', function() {
		window.location.href = $("nav[role=menu] a.cv[data-slug=school]").attr("href");
	});

	Mousetrap.bind('g w', function() {
		window.location.href = $("nav[role=menu] a.cv[data-slug=work]").attr("href");
	});

	Mousetrap.bind('g c', function() {
		window.location.href = $("nav[role=menu] a.cv[data-slug=church]").attr("href");
	});


	// Item toggles
	// --------------------------------------------------

	// Checkbox
	$("#content").on("tap", "ul.items li.item .checkbox", function(e) {
		if ($(this).attr("in-progress") != "true") {
			$(this).attr("in-progress", "true");

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
					item.attr("in-progress", "");
					item.toggleClass("checked");
					return false;
				},
				error: function(data) {
					item.attr("in-progress", "");
					console.log("error :(", data);
					return false;
				},
			});
		}

		e.preventDefault();

		return false;
	});

	// Starring
	/*
	$("#content").on("flick", "li.item .wrapper > label", function(e) {
		if ($(this).attr("in-progress") != "true") {
			$(this).attr("in-progress", "true");

			var item = $(this);
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
					item.attr("in-progress", "");
					star.toggleClass("hide");
				},
				error: function(data) {
					item.attr("in-progress", "");
					console.log("error :(", data);
					return false;
				},
			});
		}

		e.preventDefault();

		return false;
	});
	*/


	// Sorting items in a list
	// --------------------------------------------------

	function updateSort(e) {
		var item = $(e.item);
		var order = [];
		var itemList = item.closest("ul.items");
		var items = itemList.find("li.item");
		var target = itemList.attr("data-target");

		for (var i=0; i<items.length; i++) {
			var item = $(items[i]);
			order.push(parseInt(item.attr("data-item-id")));
		}

		var url = itemList.attr("data-sort-uri");

		var data = {
			ids: order.join(','),
			key: config.apiKey,
			list: target,
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
	}

	var itemLists = $("ul.items.sortable");
	for (var i=0; i<itemLists.length; i++) {
		var itemList = itemLists[i];
		var sortable = new Sortable(itemList, {
			group: "group",
			draggable: "li.item",
			handle: ".handle",
			ghostClass: "placeholder",
			onAdd: function(e) {
				updateSort(e);
			},
			onUpdate: function(e) {
				updateSort(e);
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

	$("#content").on("doubletap", "li.item .wrapper label", function(e) {
		var controls = $(this).closest(".wrapper").find(".edit-controls");
		var labels = $(this).closest(".wrapper").find("> label, > .subtitle");

		labels.fadeOut(75, function() {
			controls.fadeIn(75, function () {
				autosize(controls.find("textarea"));
				controls.find("textarea.item-text").focus();
				controls.closest("li.item").addClass("edit");
			});
		});

		e.preventDefault();

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

		controls.closest("li.item").removeClass("edit");
	}

	$("#content").on("tap", "li.item .wrapper .edit-controls .cancel", function(e) {
		_hideEditControls($(this), true);

		e.preventDefault();

		return false;
	});

	$("#content").on("tap", "li.item .star", function(e) {
		$(this).toggleClass("selected");

		e.preventDefault();

		return false;
	});

	var fields = document.querySelectorAll('li.item .edit-controls textarea');
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('esc', function(e) {
			_hideEditControls($(e.target))
		});

		if (fields[i].className != "item-metadata") {
			Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter', 'enter'], function(e) {
				_saveItem($(e.target))

				return false;
			});
		} else {
			Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
				_saveItem($(e.target))

				return false;
			});
		}
	}

	// Save
	function _saveItem(item) {
		var controls = item.parents(".edit-controls");

		var url = controls.attr("data-update-uri");

		var label = controls.siblings("label");
		var notes = label.siblings(".subtitle.notes");

		var newText = controls.find("textarea.item-text").val().trim();
		var metadata = controls.find("textarea.item-metadata").val().trim();

		var starred = controls.parents(".wrapper").siblings(".star").hasClass("selected");
		if (starred) {
			newText += " *";
		}

		var metadataLines = metadata.split("\n");
		var selector = metadataLines[0];

		var data = {
			'key': config.apiKey,
			'text': newText,
			'selector': selector,
		};

		var remainingLines = metadataLines.slice(1);
		for (var i in remainingLines) {
			var line = remainingLines[i];
			var token = line.split(' ')[0].slice(1);
			var value = line.split(' ').slice(1).join(' ');

			data[token] = value;
		}

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

				// TODO: update date and list here

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

	$("#content").on("tap", "li.item .wrapper .edit-controls .save", function(e) {
		_saveItem($(this));

		e.preventDefault();

		return false;
	});


	// List editing
	// --------------------------------------------------

	$("#content").on("doubletap", "li.list .wrapper .subtitle", function(e) {
		var controls = $(this).closest(".wrapper").find(".edit-controls");
		var labels = $(this).closest(".wrapper").find("> a, > .subtitle");

		labels.fadeOut(75, function() {
			controls.fadeIn(75, function () {
				autosize(controls.find("textarea"));
				controls.find("textarea.list-name").focus();
				controls.closest("li.list").addClass("edit");
			});
		});

		e.preventDefault();

		return false;
	});

	function _hideListEditControls(item, fast) {
		var controls = item.parents(".edit-controls");
		var labels = controls.siblings("a, .subtitle");

		if (fast) {
			controls.hide();
			labels.show();
		} else {
			controls.fadeOut(75, function() {
				labels.fadeIn(75);
			});
		}

		controls.closest("li.list").removeClass("edit");
	}

	$("#content").on("tap", "li.list .wrapper .edit-controls .cancel", function() {
		_hideListEditControls($(this), true);

		return false;
	});

	$("#content").on("tap", "li.list .star", function() {
		$(this).toggleClass("selected");

		return false;
	});

	var fields = document.querySelectorAll('li.list .edit-controls textarea');
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('esc', function(e) {
			_hideListEditControls($(e.target))
		});

		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter', 'enter'], function(e) {
			_saveList($(e.target))

			return false;
		});
	}

	// Save
	function _saveList(list) {
		var controls = list.parents(".edit-controls");

		var url = controls.attr("data-update-uri");

		var label = controls.siblings("a");
		var subtitle = label.siblings(".subtitle");

		var newName = controls.find("textarea.list-name").val().trim();
		var metadata = controls.find("textarea.list-metadata").val().trim();

		var starred = controls.parents(".wrapper").siblings(".star").hasClass("selected");
		var forReview = controls.find(".for-review").prop("checked");
		var archive = controls.find(".archive").prop("checked");

		var selector = metadata.split("\n")[0];
		var listId = metadata.split("\n")[1].slice(4).trim();

		var data = {
			'key': config.apiKey,
			'name': newName,
			'starred': starred,
			'archive': archive,
			'for_review': forReview,
			'selector': selector,
			'id': listId,
		};
		console.log(data);

		$.ajax({
			url: url,
			method: 'POST',
			data: data,
			success: function(data) {
				if (data.list) {
					// Update the link
					label.html(data.list.name);

					// Update star
					var star = controls.closest(".wrapper").siblings(".star");
					if (data.list.starred) {
						star.removeClass("hide");
					} else {
						star.addClass("hide");
					}
				} else {
					// Archived the list, so hide it
					var theList = controls.closest(".list");

					theList.slideUp(200, function() {
						theList.remove();
					});
				}

				_hideListEditControls(list);
			},
			error: function(data) {
				console.log("error :(", data);
			},
		});

		return false;
	}

	$("#content").on("tap", "li.list .wrapper .edit-controls .save", function(e) {
		_saveList($(this));

		e.preventDefault();

		return false;
	});


	// Review mode
	// --------------------------------------------------

	if ($("#review").length > 0) {
		_loadReviewMode();
	}

	$("#review").on("tap", ".group.nav .prev", function() {
		_getPrevReviewItem();
		return false;
	});

	$("#review").on("tap", ".group.nav .next", function() {
		_getNextReviewItem();
		return false;
	});

	$("#review").on("tap", ".group.nav .savenext", function() {
		_saveReviewItem();
		return false;
	});

	$("#review").on("tap", ".group.actions span", function() {
		if (!$(this).hasClass("tolist")) {
			$(this).toggleClass("selected");
		}

		return false;
	});

	if ($("#review").length > 0) {
		Mousetrap.bind('x', function() {
			$(".group.actions .checked").toggleClass("selected");
		});

		Mousetrap.bind('s', function() {
			$(".group.actions .starred").toggleClass("selected");
		});

		Mousetrap.bind('m', function() {
			$(".group.actions .someday").toggleClass("selected");
		});

		Mousetrap.bind('l', function() {
			$(".group.actions .tolist input[type=text]").focus();
			return false;
		});

		Mousetrap.bind('p', function() {
			_getPrevReviewItem();
		});

		Mousetrap.bind('k', function() {
			_getPrevReviewItem();
		});

		Mousetrap.bind('n', function() {
			_getNextReviewItem();
		});

		Mousetrap.bind('j', function() {
			_getNextReviewItem();
		});

		Mousetrap.bind('enter', function() {
			_saveReviewItem();
		});

		$("#review").on("keyup", ".group.actions .tolist input[type=text]", function(e) {
			if (e.which == 13) {
				$(this).blur();
				_saveReviewItem();
				return false;
			} else if (e.which == 27) {
				$(this).blur();
				return false;
			}

			var content = $(this).val().trim();
			var span = $(this).closest("span.tolist");

			if (content.length > 0) {
				span.addClass("selected");
			} else {
				span.removeClass("selected");
			}
		});
	}
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
	var listSlugs = $("#page-data").attr("data-list-slugs");

	if (contextSlug != '') data['context'] = contextSlug;
	if (listSlugs != '') data['lists'] = listSlugs;

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


// Review mode
// --------------------------------------------------

function _loadReviewMode() {
	var url = $("#review").data("uri");

	$.ajax({
		url: url,
		method: 'GET',
		success: function(data) {
			for (i in data.items) {
				var item = data.items[i];
			}
			_startReviewMode(data.items);
		},
		error: function(data) {
			console.log("error :(", data);
		},
	});
}

var currentReviewItemIndex;
var reviewItems;

function _startReviewMode(items) {
	// Save to global variable
	reviewItems = items;

	if (reviewItems.length > 0) {
		// Load the first item
		_loadReviewItem(0);
	}
}

function _loadReviewItem(index) {
	// Make sure the item exists
	if (typeof reviewItems[index] != "undefined") {
		currentReviewItemIndex = index;
		var item = reviewItems[index];

		// Controls
		html = "<section class='controls'>";
		html += "<div class='group nav'>";
		html += "<span class='prev'>Previous</span>";
		html += "<span class='next'>Next</span>";
		html += "<span class='savenext'>Save &amp; Next</span>";
		html += "</div>";
		html += "<div class='group actions'>";
		html += "<span class='checked'><span class='icon checked'>&#x25a1;</span></span>";
		html += "<span class='starred";
		if (item.starred) {
			html += " selected";
		}
		html += "'><span class='icon starred'>&#x2605;</span> </span>";
		html += "<span class='someday'><span class='icon'>&rarr;</span> Someday</span>";
		html += "<span class='tolist'><span class='icon'>&rarr;</span> <input type='text' /></span>";
		html += "</div>";
		html += "</section>";

		html += "<section class='metadata'>";
		html += (index + 1) + " of " + reviewItems.length;
		html += "</section>";

		html += "<div class='item'>";
		html += "<div class='selector'><a class='context' href='" + item.context_url + "'>" + item.context_slug + "</a> <a class='list' href='" + item.list_url + "'>" + item.list_slug + "</a></div>";
		html += "<div class='name'>" + item.name + "</div>";
		if (item.notes) html += "<div class='notes'>" + item.notes + "</div>";
		html += "</div>";

		$("#review").html(html);

		$("#review").attr("data-item-id", item.id);
	}
}

function _getNextReviewItem() {
	if (currentReviewItemIndex < reviewItems.length - 1) {
		_loadReviewItem(currentReviewItemIndex + 1);
	}
}

function _getPrevReviewItem() {
	if (currentReviewItemIndex > 0) {
		_loadReviewItem(currentReviewItemIndex - 1);
	}
}

function _saveReviewItem() {
	var itemId = $("#review").attr("data-item-id");

	var url = $("#review").data("update-uri");
	url = url.replace("-1", itemId);

	// Checked
	var checked = $("#review .group.actions .checked").hasClass("selected");

	// Starred
	var starred = $("#review .group.actions .starred").hasClass("selected");

	// Someday
	var someday = $("#review .group.actions .someday").hasClass("selected");

	// Move to list
	var toList = $("#review .group.actions .tolist input[type=text]").val().trim();
	if (toList.length > 0 && toList.slice(0, 1) != "::") {
		toList = "::" + toList;
	}

	var data = {
		'checked': checked,
		'starred': starred,
		'someday': someday,
		'to_list': toList,
		'key': config.apiKey,
		'review_mode': true,
	};

	$.ajax({
		url: url,
		method: 'POST',
		data: data,
		success: function(data) {
			$("#review .item .name").fadeOut(150, function() {
				// Get the next review item
				_getNextReviewItem();
			});
		},
		error: function(data) {
			$("<div class='error'>Error: " + data + "</div>").appendTo("#review");
			console.log("error :(", data);
		},
	});

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

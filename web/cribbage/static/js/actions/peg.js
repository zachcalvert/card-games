export function renderCurrentTurnDisplay(player, action) {
  $('#action-button').html(action);
  if (player === 'all') {
    $(".player-status").find('button.btn-outline-warning').remove();
    $(".player-status").append('<button class="btn btn-outline-warning btn-sm disabled">' + action + '</button>');
    $('#action-button').prop('disabled', false);
  }
  else {
    // disable current turn display for all
    $(".player-status").find('button.btn-outline-warning').remove();
    $('#action-button').prop('disabled', true);

    // enable current turn display for player
    if ((action === 'PASS' || action === 'PLAY')) {
      $('#' + player).find(".player-status").append('<button class="btn btn-outline-warning btn-sm disabled">TURN</button>');
    } else {
      $('#' + player).find(".player-status").append('<button class="btn btn-outline-warning btn-sm disabled">' + action + '</button>');
    }
    if (player === sessionStorage.getItem('nickname')) {
      $('#action-button').prop('disabled', false);
    }
  }

  if (action === 'SCORE') {
    let playedCards = $('.played');
    $.each(playedCards, function(index, card) {
      $(card).removeClass('played');
      let dealtArea = $(card).parent().parent().find('.player-cards');
      $(dealtArea).append(card);
    });
    $('.play-pile').remove();
    $('.player-cards').removeClass('col-6').addClass('col-12').css('text-align', 'center');
    $('#play-total').fadeOut(500, 'swing');
    $('.count-text').fadeOut(500, 'swing');
  }
}

function moveCardFromHandToPlayArea(card, nickname) {
  let handCard = $('#' + card);
  handCard.removeClass('to-be-played').addClass('played');
  $('#' + nickname).find('.play-pile').append(handCard);
  if (nickname === sessionStorage.getItem('nickname')) {
    handCard.removeClass('selected');
    $(handCard).css('margin-top', '0px');
  } else {
    handCard.attr("src",'/static/img/cards/' + card);
  }
}

function updateRunningTotal(new_total) {
  let current = $("#play-total").text();

  $({someValue: current}).animate({someValue: new_total}, {
    duration: 200,
    easing:'swing', // can be anything
    step: function() { // called on every step
      // Update the element's text with rounded-up value:
      $('#play-total').text(Math.round(this.someValue));
    }
  });
}

export function peg(msg) {
  moveCardFromHandToPlayArea(msg.card, msg.nickname);
  updateRunningTotal(msg.new_total);
}

export function clearPeggingArea() {
  $('#play-total').html(0);
}

export function invalidCard(card) {
  $('#' + card).parent().toggleClass('selected');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function updatePlayerStatus(player, status) {
  // don't display the go message to the player who passed
  if (status === 'GO' && player === sessionStorage.getItem('nickname')) {
    return;
  }

  let playerHeading = $('#' + player);
  let statusUpdate = $('<div/>', {
    class: 'player-status-update',
    html: status
  });
  playerHeading.prepend(statusUpdate);
  await sleep(1000);
  statusUpdate.fadeOut(1000, 'swing');
}

export async function updateCribStatus(status) {
  // hide the crib heading text, display the score, and re-display the crib heading text
  let cribArea = $('.crib');
  let statusUpdate = $('<div/>', {
    class: 'crib-status-update',
    html: status
  });
  $('.crib').find('.panel-heading').css('color', 'rgb(21, 32, 43)');
  cribArea.prepend(statusUpdate);
  await sleep(1000);
  statusUpdate.fadeOut(1000, function() {
     $('.crib').find('.panel-heading').css('color', 'white');
  });
}



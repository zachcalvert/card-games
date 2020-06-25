export function renderCurrentTurnDisplay(player, action) {
  console.log('Time for ' + player + ' to ' + action);
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
    $('#' + player).find(".player-status").append('<button class="btn btn-outline-warning btn-sm disabled">' + action + '</button>');
    if (player === sessionStorage.getItem('nickname')) {
      $('#action-button').prop('disabled', false);
    }
  }

  if (action === 'SCORE') {
    let playedCards = $('.played')
    $.each(playedCards, function(index, card) {
      let dealtArea = $(card).parent().parent().find('.col-9')
      dealtArea.append(card);
    });
    $('.player-cards').removeClass('col-9').addClass('col-12');
    $('.opponent-cards').removeClass('col-9').addClass('col-12');
    $('.play-pile').remove();
    $('#play-total').text('');
  }
}

function moveCardFromHandToPlayArea(card, nickname) {
  let handCard = $('#' + card);
  console.log('requested to move from hand to play area');
  handCard.addClass('played');
  $('#' + nickname).find('.play-pile').append(handCard);
  if (nickname === sessionStorage.getItem('nickname')) {
    handCard.removeClass('selected');
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
  console.log('Im clearing the pegging area');
  $('#play-total').html(0);
  console.log('pegging area cleared');
}

export function invalidCard(card) {
  $('#' + card).parent().toggleClass('selected');
}
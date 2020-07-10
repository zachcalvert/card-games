export function renderCurrentTurnDisplay(player, action) {
  let actionButton = $('#action-button');
  let playerStatuses = $(".player-status");
  actionButton.html(action);
  playerStatuses.find('button.btn-outline-warning').remove();
  if (player === 'all') {
    actionButton.prop('disabled', false);
  }
  else {
    actionButton.prop('disabled', true);

    // enable current turn display for player
    if ((action === 'PASS' || action === 'PLAY')) {
      $('#' + player).find(".player-status").append('<button class="btn btn-outline-warning btn-sm disabled">TURN</button>');
    }
    if (player === sessionStorage.getItem('nickname')) {
      actionButton.prop('disabled', false);
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
    $('.player-cards').removeClass('col-2').addClass('col-12').css('text-align', 'center');
    $('#play-total').fadeOut(500, 'swing');
    $('.count-text').fadeOut(500, 'swing');
  }
}

function moveCardFromHandToPlayArea(card, nickname) {
  let handCard = $('#' + card);
  let playPile = $('#' + nickname).find('.play-pile');
  let toBePlayed = $('#' + nickname).find('.player-cards');

  handCard.removeClass('to-be-played').addClass('played');
  playPile.append(handCard);

  console.log('num played cards is ' + playPile.children().length)
  switch  (playPile.children().length) {
    case 1:
      playPile.removeClass('col-2').addClass('col-4');
      toBePlayed.removeClass('col-10').addClass('col-8');
      break;
    case 2:
      playPile.removeClass('col-4').addClass('col-6');
      toBePlayed.removeClass('col-8').addClass('col-6');
      break;
    case 3:
      playPile.removeClass('col-6').addClass('col-8');
      toBePlayed.removeClass('col-6').addClass('col-4');
      break;
    case 4:
      playPile.removeClass('col-8').addClass('col-10');
      toBePlayed.removeClass('col-4').addClass('col-2');
      break;
    default:
      // code block
  }

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

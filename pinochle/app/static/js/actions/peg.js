export function renderCurrentTurnDisplay(player, action) {
  let actionButton = $('#action-button');
  actionButton.html(action);

  if (player === 'all') {
    actionButton.prop('disabled', false);
  } else if (player === sessionStorage.getItem('nickname')) {
    actionButton.prop('disabled', false);
  }
}

function moveCardFromHandToPlayArea(card, nickname) {
  let handCard = $('#' + card);
  let playPile = $('#' + nickname).find('.play-pile');
  handCard.removeClass('to-be-played').addClass('played');
  playPile.append(handCard);

  if (nickname === sessionStorage.getItem('nickname')) {
    console.log('something');
  } else {
    handCard.attr("src",'/static/img/cards/' + card);
  }
}

export function play(msg) {
  moveCardFromHandToPlayArea(msg.card, msg.nickname);
}

export function invalidCard(card) {
  $('#' + card).parent().toggleClass('selected');
}
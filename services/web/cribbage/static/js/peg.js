export function removeCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
  $('#' + player + ' #action-button').text('Play').prop('disabled', true);
}

export function renderCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', '#1CA1F2');
  $('#' + player + ' #action-button').text('Play').prop('disabled', false);
}

export function moveCardFromHandToTable(card) {
  let handCard = $('#' + card.id);
  handCard.parent().removeClass('selected');
  handCard.hide();

  let cardImage = $('<img/>', {
    id: card.id,
    class: 'playedCard',
    src: '/static/img/cards/' + card.hash
  });
  $('#play-area').append(cardImage);
}

export function showCardPlayScore(cardId, points) {
  return;
}

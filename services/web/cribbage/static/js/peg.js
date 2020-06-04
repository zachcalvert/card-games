export function removeCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
  $('#' + player + ' #action-button').text('Play').prop('disabled', true);
}

export function renderCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'pink');
  $('#' + player + ' #action-button').text('Play').prop('disabled', false);
}

export function moveCardFromHandToTable(msg) {
  let cardImage = $('<img/>', {
    class: 'playerCard',
    src: msg.card_image
  });
  $('.cribbage-table').append(cardImage);

  let card = $('#' + msg.card_id);
  card.parent().removeClass('selected');
  card.hide();
}

export function showCardPlayScore(msg) {
  return;
}

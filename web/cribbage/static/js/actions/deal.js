export function deal(msg) {
  $.each(msg.hands, function(player, cards) {
    if (player === sessionStorage.getItem('nickname')) {
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card,
          class: 'playerCard',
          src: '/static/img/cards/' + card
        });
        $('#' + player + '-cards').append(cardImage);
      });
    } else {
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card,
          class: 'opponentCard',
          src: '/static/img/cards/facedown.png'
        });
        $('#' + player + '-cards').append(cardImage);
      });
    }
  });
};
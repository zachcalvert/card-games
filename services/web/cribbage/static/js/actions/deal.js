export function deal(msg) {
  $.each(msg.hands, function(player, cards) {
    if (player === sessionStorage.getItem('nickname')) {
      let card_hashes = []
      console.log(cards);
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card,
          class: 'playerCard',
          src: '/static/img/cards/' + card
        });
        let cardListItem = $('<li/>', {
          class: 'list-group-item',
        });
        cardListItem.append(cardImage)
        $('#' + player + '-cards').append(cardListItem);
        card_hashes.push(card)
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
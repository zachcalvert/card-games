export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length === 0) {
    let playerName = $('<span/>', {
      class: 'player-nickname',
      html: msg.nickname
    });

    let playerStatus = $('<span/>', {
      class: 'player-status',
    });

    let panelHeading = $('<div/>', {
      class: 'panel-heading',
    });
    panelHeading.append(playerName);
    panelHeading.append(playerStatus);

    let opponentCards = $('<div/>', {
      id: msg.nickname + '-cards',
      class: 'opponent-cards col-12',
    });
    let panelBody = $('<div/>', {
      class: 'row opponent-play-area panel-body'
    });
    panelBody.append(opponentCards);

    let opponentPanel = $('<div/>', {
      id: msg.nickname,
      class: 'opponent rounded panel panel-default',
    });
    opponentPanel.append(panelHeading);
    opponentPanel.append(panelBody);
    $('.opponents').append(opponentPanel);

    $('.game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}
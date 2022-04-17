// COMP6080 Assignment 2
// By z5161194
// Javascript file for Slackr

import { BACKEND_PORT } from './config.js';
import { fileToDataUrl } from './helpers.js';

console.log('Let\'s go!');

/********************************
 *          Variables           *
 ********************************/

const host = 'http://localhost:5005/';

var TOKEN;
const setToken = (token) => {
    TOKEN = token;
}

var NAME;
const setName = (name) => {
    NAME = name;
}

var USER_ID;
const setUserId = (id) => {
    USER_ID = id;
}

var CURR_CHANNEL_ID = null;
const setChannelId = (id) => {
    CURR_CHANNEL_ID = id;
}

var CHANNELS = new Array();
const setChannels = (channels) => {
    CHANNELS = channels;
}

var MESSAGE_COUNTER = 0;
const setMessageCounter = (num) => {
    MESSAGE_COUNTER = num;
}

/********************************
 *      Helper functions        *
 ********************************/

// converts ISO string to date
//      Source: https://stackoverflow.com/questions/27012854/how-to-change-iso-date-string-to-date-object
function ISOtoDate(s) {
    var b = s.split(/\D+/);
    return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
}

// Returns a user friendly date time string
const getDateTime = (data) => {
    var date;
    if (data) {
        date = ISOtoDate(data);
    } else {
        date = new Date();
    }

    return date.getDate() + "/"
        + (date.getMonth()+1)  + "/"
        + date.getFullYear() + " @ "
        + date.getHours() + ":"
        + date.getMinutes() + ":"
        + date.getSeconds();
}

// Helper function for fetch
const apiFetch = (method, path, token, body) => {
    const request = {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
    };
    if (token !== null) {
        request.headers['Authorization'] = `Bearer ${token}`;
    }

    console.log(request);

    return new Promise((resolve, reject) => {
        // have to call either resolve or reject
        fetch(host + path, request)
        .then((response) => {
            if (response.status === 400 || response.status === 403) {
                response.json().then((errorMsg) => {
                    reject(errorMsg['error']);
                });
            } else if (response.status === 200) {
                return response.json().then(data => {
                    resolve(data);
                });
            }
        })
        .catch((err) => {
            console.log(err);
        });
    });
}

// Error popup
const error = (message) => {
    var popup = new bootstrap.Modal(document.getElementById('error-popup'));
    document.getElementById('error-message').textContent = message;
    // document.getElementById('error-popup').style.display = 'block';
    popup.show();
}

// Returns true if current user is a member of given channel
const isMember = (channel) => {
    for (var member of channel.members) {
        if (member === USER_ID) return true;
    }
    return false;
}



/**********************************************
 *      M1: register & login functions        *
 **********************************************/

// Login page
document.getElementById('log-in').addEventListener('click', (event) => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    console.log(email, password);

    const body = {
        email: email,
        password: password,
    };

    apiFetch('POST','auth/login', null, body)
    .then((data) => {
        console.log(data);
        setToken(data['token']);
        setUserId(data['userId']);

        // Hiding log in page
        const loginPage = document.getElementsByClassName('registration-login');
        for (var element of loginPage) {
            element.style.display = 'none';
        }

        // Render homepage
        homepage();
    })
    .catch((err) => {
        console.log(err);
    });
});

// Register page
document.getElementById('create-account').addEventListener('click', () => {
    document.getElementById('page-login').style.display = 'none';
    document.getElementById('page-register').style.display = 'flex';
});

document.getElementById('existing-user').addEventListener('click', () => {
    document.getElementById('page-login').style.display = 'flex';
    document.getElementById('page-register').style.display = 'none';
});

document.getElementById('register').addEventListener('click', () => {
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const passwordConfirm = document.getElementById('reg-password-confirm').value;
    const name = document.getElementById('reg-name').value;
    console.log(email, password, name);

    if (name === "") {
        error("Please enter a name");
        return;
    } else if (email === "") {
        error("Please enter an email");
        return;
    } else if (password === "") {
        error("Please enter a password");
        return;
    } else if (password !== passwordConfirm) {
        error("Password must match, please try again");
        return;
    }

    const body = {
        email: email,
        password: password,
        name: name,
    };

    apiFetch('POST','auth/register', null, body)
    .then((data) => {
        document.getElementById("page-register").style.display = "none";
        setToken(data['token']);
        setUserId(data['userId']);
        homepage();
    })
    .catch((data) => {
        console.log(data);
    });
});

// Sign out button
document.getElementById("sign-out").addEventListener("click", () => {
    apiFetch('POST', 'auth/logout', TOKEN);
    setToken(null);
    setUserId(null);
    setChannelId(null);

    document.getElementById('slackr-header').style.display = "block";
    document.getElementById('homepage-container').style.display = "none";
    document.getElementById('page-login').style.display = "flex";
});

/************************************************
 *      M2: Creating and viewing channels       *
 ************************************************/
// Homepage
const homepage = () => {
    document.getElementById("slackr-header").style.display = "none";
    document.getElementById("navbar").style.display = "block";
    getUser(USER_ID)
    .then(({name}) => {
        document.getElementById("username").innerText = name;
    })

    const homepage = document.getElementById('homepage-container');
    homepage.style.display = 'flex';

    apiFetch('GET','channel', TOKEN)
    .then((data) => {
        // Appending channels to homepage sidebar
        setupChannels(data.channels);
    })
    .catch((err) => {
        console.log(err);
    });
}

// Returns a promise containing user data
const getUser = (userId) => {
    return new Promise ((resolve, reject) => {
        apiFetch('GET', `user/${userId}`, TOKEN)
        .then(data => {
            resolve(data);
        })
        .catch(err => {
            reject(err);
        })
    })
}

// Navbar
document.getElementById('toggle').addEventListener('click', () => {
    const sidebar = document.getElementById('sidebar');
    const messageBox = document.getElementById('message-box');
    if (sidebar.style.display === "flex") {
        sidebar.style.display = "none";
        messageBox.style.width = "98%";
    } else {
        sidebar.style.display = "flex";
        messageBox.style.width = "80%";
    }
});

// Setting up the channel sidebar
const setupChannels = (channels) => {
    const channelsPublic = document.getElementById('channels-public');
    const channelsPrivate = document.getElementById('channels-private');

    channelsPublic.innerText = "";
    channelsPrivate.innerText = "";
    console.log(channelsPublic);

    for (var ch of channels) {
        var channel = document.getElementById("template-channel-button").cloneNode(true);
        channel.childNodes[1].innerText = ch.name;
        channel.id = ch.id.toString();
        if (ch.private) {
            if(isMember(ch)) channelsPrivate.appendChild(channel);
        } else {
            channelsPublic.appendChild(channel);
        }
        configureChannelBtns(channel.id);
    };
}

// Sets the homepage main content display value
const mainContentDisplay = (display) => {
    document.getElementById("main-content").style.display = display;
}

// Adds event listener to channel with given id
const configureChannelBtns = (id) => {
    const channel = document.getElementById(id);
    if (channel === null) return;
    channel.addEventListener("click", () => {
        if (CURR_CHANNEL_ID === id) {
            mainContentDisplay("none");
            setChannelStatus(CURR_CHANNEL_ID, "inactive");
            CURR_CHANNEL_ID = null;
            document.getElementById('main-placeholder').style.display = "block";

        } else {
            renderChannel(id);
            document.getElementById('main-placeholder').style.display = "none";
        }
    })
}

// Renders the channel information
const renderChannel = (id) => {
    // check edit channel status
    if (document.getElementById('edit-channel-cancel').style.display === "inline") {
        editChannelCancel();
    }

    mainContentDisplay("none");

    const channelName = document.getElementById("channel-name");
    const channelDescription = document.getElementById("channel-description");
    const channelTimestamp = document.getElementById("channel-timestamp");
    const channelOwner = document.getElementById("channel-owner");

    if (CURR_CHANNEL_ID !== null) {
        setChannelStatus(CURR_CHANNEL_ID, "inactive");
    }

    // reset pins
    const pinnedContainer = document.getElementById("pinned-message-container");
    pinnedContainer.innerText = "";

    // Set the current id to current channel
    setChannelId(id);
    setChannelStatus(CURR_CHANNEL_ID, "active");

    apiFetch('GET',`channel/${id}`, TOKEN)
    .then((data) => {
        channelName.innerText = data.name;
        channelDescription.innerText = data.description;
        channelTimestamp.innerText = getDateTime(data.createdAt);
        setChannelType(data.private);

        mainContentDisplay("flex");

        renderMessages(id);

        return apiFetch('GET', `user/${data.creator}`, TOKEN);
    })
    .then((data) => {
        channelOwner.innerText = data.name;
    })
    .catch((err) => {
        if (err === "Authorised user is not a member of this channel")joinChannelPopup();
    });
}

// Displays the join channel modal
const joinChannelPopup = () => {
    const popup = new bootstrap.Modal(document.getElementById('join-channel-popup'));
    popup.show();
}

// Join channel button
document.getElementById('join-channel-button').addEventListener('click', () => {
    console.log(CURR_CHANNEL_ID);
    apiFetch('POST', `channel/${CURR_CHANNEL_ID}/join`, TOKEN)
    .then(() => {
        renderChannel(CURR_CHANNEL_ID);
    })
    .catch(err => {
        error(err);
    });
});

// Reject join channel button
document.getElementById('reject-join-channel').addEventListener('click', () => {
    setChannelStatus(CURR_CHANNEL_ID, "inactive");
    setChannelId(null);
});

// Providing the channel information banner with the channel type
const setChannelType = (isPrivate) => {
    const channelType = document.getElementById("channel-type");
    if (isPrivate) {
        channelType.innerText = "Private";
        channelType.classList.replace("bg-light", "bg-dark");
        channelType.classList.remove("text-black");
    } else {
        channelType.innerText = "Public";
        channelType.classList.replace("bg-dark", "bg-light");
        channelType.classList.add("text-black");
    }
}

// Edit channel name and descriptor
document.getElementById("edit-channel-button").addEventListener('click', () => {
    const btn = document.getElementById("edit-channel-button");
    const cancel = document.getElementById("edit-channel-cancel");
    const newName = document.getElementById("edited-channel-name");
    const newDescription = document.getElementById("edited-channel-description");
    const container = document.getElementById("edit-channel");
    const channelName = document.getElementById("channel-name");
    const channelDescription = document.getElementById("channel-description");

    if (btn.innerText === "Edit") {
        document.getElementById("leave-channel-button").style.display = "none";
        btn.innerText = "Save";
        btn.classList.replace("btn-outline-dark", "btn-success");
        container.style.display = "flex";
        channelName.style.display = "none";
        cancel.style.display = "inline";
        channelDescription.style.display = "none";
        document.getElementById("leave-channel-button").style.display = "none";
    } else {

        if (newName.value === "") {
            error("Please enter a valid channel name");
        } else {
            document.getElementById("leave-channel-button").style.display = "inline";

            channelName.innerText = newName.value;
            channelDescription.innerText = newDescription.value;
            console.log(newDescription);

            btn.innerText = "Edit";
            btn.classList.replace("btn-success", "btn-outline-dark");
            container.style.display = "none";
            channelName.style.display = "block";
            channelDescription.style.display = "block";
            cancel.style.display = "none";

            // fetch call
            const body = {
                name: channelName.innerText,
                description: channelDescription.innerText,
            }
            apiFetch('PUT', `channel/${CURR_CHANNEL_ID}`, TOKEN, body)
            .then(data => {
                console.log(data);
            })
            .catch(err => {
                console.log(err);
            });
        }
    }
});

// Cancel channel edit
document.getElementById("edit-channel-cancel").addEventListener('click', () => {
    editChannelCancel();
})

// Helper function that cancels the channel edit
const editChannelCancel = () => {
    document.getElementById("edit-channel").style.display = "none";
    document.getElementById("channel-name").style.display = "block";
    document.getElementById("channel-description").style.display = "block";
    document.getElementById("leave-channel-button").style.display = "inline";
    document.getElementById("edit-channel-cancel").style.display = "none";

    const btn = document.getElementById("edit-channel-button");
    btn.innerText = "Edit";
    btn.classList.replace("btn-success", "btn-outline-dark");
}

// Leave channel
document.getElementById("leave-channel-button").addEventListener('click', () => {
    apiFetch('POST', `channel/${CURR_CHANNEL_ID}/leave`, TOKEN)
    .then(data => {
        mainContentDisplay("none");
        homepage();
        // document.getElementById(`${CURR_CHANNEL_ID}`).remove();
        setChannelId(null);
    })
    .catch(err => {
        error(err);
    })
})

// Change the user interface status
//      - status input: 'active' or 'inactive'
const setChannelStatus = (id, status) => {
    if (id === null) return;
    const channel = document.getElementById(id);
    if (status === "active") {
        channel.classList.add("channel-active");
    } else {
        channel.classList.remove("channel-active");
    }
}

// New channel page
document.getElementById('new-channel-button').addEventListener('click', () => {
    document.getElementById('new-channel-form').style.display = 'block';
    document.getElementById('slackr-header').style.display = 'block';
    document.getElementById('homepage-container').style.display = 'none';
});

// Cancel new channel creation
document.getElementById('new-channel-cancel').addEventListener('click', () => {
    document.getElementById('new-channel-form').style.display = 'none';
    document.getElementById('slackr-header').style.display = 'none';
    homepage();
});

// Create new channel
document.getElementById('new-channel-create').addEventListener('click', () => {
    const name = document.getElementById('new-channel-name');
    const description = document.getElementById('new-channel-description');
    const type = document.getElementById('new-channel-type');

    if (name.value === "") {
        error('Please enter a channel name');
        return;
    }

    const body = {
        name: name.value,
        private: (type.value === "Private"),
        description: description.value,
    };

    name.value = "";
    description.value = "";

    apiFetch('POST', 'channel', TOKEN, body)
    .then((data) => {
        document.getElementById('new-channel-form').style.display = 'none';
        homepage();
    })
    .catch((err) => {
        console.log(err);
    });

});


/************************************
 *      M3: Channel Messages        *
 ************************************/

// Show Messages
const renderMessages = (id) => {

    const channelMessages = document.getElementById('channel-messages');
    const paginateButton = document.getElementById('paginate');

    setMessageCounter(0);

    // removing previous messages
    channelMessages.innerText = "";

    // rendering messages from channel
    getMessages(id, 0)
    .then(data => {
        console.log(data);
        if (data.messages.length >= 25) {
            paginateButton.style.display = 'block';
        } else {
            paginateButton.style.display = 'none';
        }
        for (var msg of data.messages) {
            console.log(msg);
            appendMessage(msg, 'after');
        }
    })
    .catch(err => {
        error('error in renderMessages' + err);
    });
}

// Returns a promise with message data
const getMessages = (id, index) => {
    return new Promise((resolve, reject) => {
            apiFetch('GET', `message/${id}?start=${index}`, TOKEN)
            .then((data) => {
                resolve(data);
                console.log(data);
            })
            .catch(err => {
                reject(err);
            });
        });
}

// appends a single message to the parent channel
//      - input: msg in json format
const appendMessage = (msg, location) => {
    const channelMessages = document.getElementById('channel-messages');
    const message = document.getElementById("template-message").cloneNode(true);
    const messageInfo = message.childNodes[1].childNodes[1].childNodes;
    const paginateButton = document.getElementById('paginate');

    message.id = msg.id;
    messageInfo[3].innerText = getDateTime(msg.sentAt);
    message.childNodes[5].innerText = msg.message;

    if (msg.image !== undefined) {
        message.childNodes[1].childNodes[5].src = msg.image;
    }

    if (msg.sender === USER_ID) {
        // display message buttons
        message.childNodes[1].childNodes[3].style.display = "block";

        // change positioning of profile image for style
        message.childNodes[1].childNodes[5].style.position = "relative";
    }

    apiFetch('GET', `user/${msg.sender}`, TOKEN)
    .then(data => {
        console.log(data);
        console.log(messageInfo);

        messageInfo[1].innerText = data.name;

        if (location === "after") {
            channelMessages.appendChild(message);
        } else if (location === "before") {
            channelMessages.prepend(message);
        }

        if (msg.pinned) {
            pin(msg.id.toString());
        }

        configureEditMessage(msg.id.toString());
        configureDeleteMessage(msg.id.toString());
        configurePinMessage(msg.id.toString());
        configureReactMessage(msg.id.toString());
        setMessageCounter(MESSAGE_COUNTER+1);

        for (var r of msg.reacts) {
            if (r.user === USER_ID) {
                interfaceReact(msg.id, r.react);
            }
        }

    })
    .catch(err => {
        error('error in appendMessage ' + err);
    });
}

// Sending Messages
document.getElementById("message-input").addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Send message button
document.getElementById("send-message-button").addEventListener('click', () => {
    sendMessage();
});

// Send message helper function
const sendMessage = () => {
    const textInput = document.getElementById("message-input");
    const message = textInput.value;
    var image = document.getElementById("profile-img").src;

    if (message.replace(/\s+/g, "") === "") {
        error("Message must contain text");
        return;
    }

    console.log(image);
    if (image !== "") {
        var body = {
            message: message,
            image: image,
        }
    } else {
        var body = {
            message: message,
        }
    }

    apiFetch('POST', `message/${CURR_CHANNEL_ID}`, TOKEN, body)
    .then(() => {
        textInput.value = "";
        return getMessages(CURR_CHANNEL_ID, 0);
    })
    .then(({messages}) => {
        appendMessage(messages[0], 'before');
    })
    .catch(err => {
        error(err);
    });
}

// Editing a message
const configureEditMessage = (msgId) => {
    const message = document.getElementById(msgId);

    if (message === null) return;
    const editButton = message.childNodes[1].childNodes[3].childNodes[1];
    const cancelEdit = message.childNodes[1].childNodes[3].childNodes[5];
    const msgInput = message.childNodes[7].childNodes[1];
    const existingMsg = message.childNodes[5];

    cancelEdit.addEventListener('click', () => {
        toggleEditBtn(msgId);
    });

    editButton.addEventListener('click', (event) => {
        if (event.target.innerText === 'Edit') {
            toggleEditBtn(msgId);
        } else {
            var body;
            var image = document.getElementById("profile-img").src;

            if (msgInput.value.replace(/\s+/g, "") === "") {
                error("Message must contain text");
                return;
            } else if (msgInput.value === existingMsg.innerText) {
                error("Message must not be identical to existing message");
                return;
            }

            console.log(image, msgInput.value);
            if (image !== "") {
                body = {
                    message: msgInput.value,
                    image: image,
                }
            } else {
                body = {
                    message: msgInput.value,
                }
            }

            apiFetch('PUT', `message/${CURR_CHANNEL_ID}/${msgId}`, TOKEN, body)
            .then(data => {
                console.log(data);
            })
            .catch(err => {
                error('error in config edit' + err);
            });


            toggleEditBtn(msgId);
            const editedTimestamp = message.childNodes[9].childNodes[1].childNodes[1];
            message.childNodes[9].style.display = "block";
            editedTimestamp.innerText = getDateTime();
            existingMsg.innerText = msgInput.value;
        }
    });
}

// Deleting a message
const configureDeleteMessage = (msgId) => {
    const message = document.getElementById(msgId);
    const deleteButton = message.childNodes[1].childNodes[3].childNodes[3];
    const channelMessages = document.getElementById("channel-messages");

    deleteButton.addEventListener('click', () => {
        apiFetch('DELETE', `message/${CURR_CHANNEL_ID}/${msgId}`, TOKEN)
        .then(() => {
            channelMessages.removeChild(document.getElementById(msgId.toString()));
        })
        .catch(err => {
            error('error in config delete: ' + err);
        });
    });
}

// Pin a message
const configurePinMessage = (msgId) => {
    const message = document.getElementById(msgId);
    const element = message.getElementsByClassName('pin')[0];

    element.addEventListener('click', () => {
        if (element.classList.contains("pin-active")) {
            apiFetch('POST',`message/unpin/${CURR_CHANNEL_ID}/${msgId}`, TOKEN)
            .then(() => {
                unpin(msgId);
            })
            .catch(err => {
                error(err);
            });
        } else {
            apiFetch('POST',`message/pin/${CURR_CHANNEL_ID}/${msgId}`, TOKEN)
            .then(() => {
                pin(msgId);
            })
            .catch(err => {
                error(err);
            });
        }
    });
}

// Pins a message with given id
const pin = (msgId) => {
    console.log(msgId);
    const message = document.getElementById(msgId);
    console.log(message);
    const pin = message.getElementsByClassName('pin')[0];
    const pinnedContainer = document.getElementById("pinned-message-container");

    pin.classList.add("pin-active");
    const clone = message.cloneNode(true);
    clone.id = `clone-${msgId}`;
    pinnedContainer.appendChild(clone);
}

// Unpins a message with given id
const unpin = (msgId) => {
    const message = document.getElementById(msgId);
    const pin = message.getElementsByClassName('pin')[0];
    const pinnedContainer = document.getElementById("pinned-message-container");

    pin.classList.remove("pin-active");
    const clone = document.getElementById(`clone-${msgId}`);
    pinnedContainer.removeChild(clone);
}

// React to a message
const configureReactMessage = (msgId) => {
    const message = document.getElementById(msgId);
    const element = message.getElementsByClassName('reacts')[0].childNodes;
    const smile = element[1];
    const laugh = element[3];
    const sad = element[5];

    smile.addEventListener('click', () => {
        if (smile.classList.contains('btn-outline-light')) {
            // react
            smile.classList.replace('btn-outline-light', 'btn-light');
            react(msgId, "smile");
        } else {
            // unreact
            smile.classList.replace('btn-light', 'btn-outline-light');
            unreact(msgId, "smile");
        }
    });

    laugh.addEventListener('click', () => {
        if (laugh.classList.contains('btn-outline-light')) {
            // react
            laugh.classList.replace('btn-outline-light', 'btn-light');
            react(msgId, "laugh");
        } else {
            // unreact
            laugh.classList.replace('btn-light', 'btn-outline-light');
            unreact(msgId, "laugh");
        }
    });

    sad.addEventListener('click', () => {
        if (sad.classList.contains('btn-outline-light')) {
            // react
            sad.classList.replace('btn-outline-light', 'btn-light');
            react(msgId, "sad");
        } else {
            // unreact
            sad.classList.replace('btn-light', 'btn-outline-light');
            unreact(msgId, "sad");
        }
    });


}

// Set up the interface for existing reacts
const interfaceReact = (msgId, reaction) => {
    const message = document.getElementById(msgId);
    const element = message.getElementsByClassName('reacts')[0].childNodes;
    const smile = element[1];
    const laugh = element[3];
    const sad = element[5];

    if (reaction === "smile") {
        smile.classList.replace('btn-outline-light', 'btn-light');
    } else if (reaction === "laugh") {
        laugh.classList.replace('btn-outline-light', 'btn-light');
    } else if (reaction ==="sad") {
        sad.classList.replace('btn-outline-light', 'btn-light');
    }
}

// React to a message with given id and reaction
const react = (msgId, reaction) => {
    const message = document.getElementById(msgId);
    const body = {
        react: reaction
    }
    apiFetch('POST', `message/react/${CURR_CHANNEL_ID}/${msgId}`, TOKEN, body)
    .then (() => {
        console.log('success react ' + reaction);
    })
    .catch (err => {
        error(err);
    })
}

// Unreact to a message with given id and reaction
const unreact = (msgId, reaction) => {
    const message = document.getElementById(msgId);
    const body = {
        react: reaction
    }
    apiFetch('POST', `message/unreact/${CURR_CHANNEL_ID}/${msgId}`, TOKEN, body)
    .then (() => {
        console.log('success Unreact ' + reaction);
    })
    .catch (err => {
        error(err);
    })
}

// Toggles edit button and textarea between save and edit
const toggleEditBtn = (msgId) => {
    const message = document.getElementById(msgId);
    const editButton = message.childNodes[1].childNodes[3].childNodes[1];
    const msgInput = message.childNodes[7].childNodes[1];
    const existingMsg = message.childNodes[5];
    const cancelEdit = message.childNodes[1].childNodes[3].childNodes[5];

    if (editButton.innerText === 'Edit') {
        existingMsg.style.display = 'none';
        msgInput.parentNode.style.display = 'block';
        msgInput.value = existingMsg.innerText;
        editButton.innerText = 'Save';
        editButton.classList.replace('btn-light', 'btn-success');
        cancelEdit.style.display = 'block';
    } else {
        existingMsg.style.display = 'block';
        msgInput.parentNode.style.display = 'none';
        msgInput.value = "";
        editButton.innerText = 'Edit';
        editButton.classList.replace('btn-success', 'btn-light');
        cancelEdit.style.display = 'none';
    }
}

// Paginate
document.getElementById('paginate').addEventListener('click', (e) => {
    const btn = document.getElementById('paginate');
    // rendering messages from channel
    getMessages(CURR_CHANNEL_ID, MESSAGE_COUNTER)
    .then(data => {
        console.log(data);
        if (data.messages.length >= 25) {
            btn.style.display = 'block';
        } else {
            btn.style.display = 'none';
        }
        for (var msg of data.messages) {
            appendMessage(msg, 'after');
        }
    })
    .catch(err => {
        error('error in renderMessages' + err);
    });
});
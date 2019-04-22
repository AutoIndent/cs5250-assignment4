
/*
 * This is example spinlock implementation with cas
 * assume integer pointed by variable "lock" is 0 at the beginning
 * value 1 means locked, 0 means unlocked
 */

void spin_lock(int *lock) {
    while(!cas(lock, 0, 1));
}

void spin_unlock(int *lock) {
    cas(lock, 1, 0);
}
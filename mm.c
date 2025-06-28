#include "proc.h"
#include "memory.h"

static void *pf = NULL;

void* new_page(void) {
  assert(pf < (void *)_heap.end);
  void *p = pf;
  pf += PGSIZE;
  return p;
}

void free_page(void *p) {
  panic("not implement yet");
}

/* The brk() system call handler. */
//resize
int mm_brk(uint32_t new_brk) {
  if (current->cur_brk != 0) {
    //extend
    if (new_brk > current->max_brk) {
      void* va;
      //brk begin and end
      void* va_begin = (void *)((current->max_brk - 1) & ~0xfff) + PGSIZE;
      void* va_end = (void *)((new_brk - 1) & ~0xfff);
  
      for (va = va_begin; va <= va_end; va += PGSIZE)
        _map(&current->as, va, new_page());
      current->max_brk = new_brk;
    }
    current->cur_brk = new_brk;
  }else if(current->cur_brk == 0){
    //first time
    current->cur_brk = new_brk;
    current->max_brk = new_brk;
  }
  return 0;
}

void init_mm() {
  pf = (void *)PGROUNDUP((uintptr_t)_heap.start);
  Log("free physical pages starting from %p", pf);

  _pte_init(new_page, free_page);
}

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { Loader2, Lock, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/api/client';

const changePasswordSchema = z.object({
  current_password: z
    .string()
    .min(1, 'Obecne hasło jest wymagane'),
  new_password: z
    .string()
    .min(8, 'Nowe hasło musi mieć co najmniej 8 znaków')
    .max(100, 'Hasło nie może być dłuższe niż 100 znaków')
    .regex(/[A-Z]/, 'Hasło musi zawierać co najmniej jedną wielką literę')
    .regex(/[a-z]/, 'Hasło musi zawierać co najmniej jedną małą literę')
    .regex(/[0-9]/, 'Hasło musi zawierać co najmniej jedną cyfrę'),
  confirm_password: z
    .string()
    .min(1, 'Potwierdzenie hasła jest wymagane'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'Hasła nie są identyczne',
  path: ['confirm_password'],
});

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export function ChangePasswordForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
  });

  const onSubmit = async (data: ChangePasswordFormData) => {
    setIsLoading(true);
    
    try {
      const response = await api.post<{ success: boolean; message?: string; error?: string }>(
        '/users/me/change-password',
        {
          current_password: data.current_password,
          new_password: data.new_password,
        }
      );

      if (response.success) {
        toast.success('Hasło zostało zmienione', {
          description: response.message || 'Twoje hasło zostało pomyślnie zaktualizowane.',
        });
        reset();
      } else {
        toast.error('Błąd zmiany hasła', {
          description: response.error || 'Nie udało się zmienić hasła.',
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Wystąpił nieoczekiwany błąd';
      toast.error('Błąd zmiany hasła', {
        description: message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    switch (field) {
      case 'current':
        setShowCurrentPassword(!showCurrentPassword);
        break;
      case 'new':
        setShowNewPassword(!showNewPassword);
        break;
      case 'confirm':
        setShowConfirmPassword(!showConfirmPassword);
        break;
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Current Password */}
      <div className="space-y-2">
        <Label htmlFor="current_password" className="text-book-brown">
          <Lock className="w-4 h-4 inline mr-2" />
          Obecne hasło
        </Label>
        <div className="relative">
          <Input
            id="current_password"
            type={showCurrentPassword ? 'text' : 'password'}
            {...register('current_password')}
            className={errors.current_password ? 'border-red-500 pr-10' : 'pr-10'}
            disabled={isLoading}
            placeholder="Wprowadź obecne hasło"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-0 top-0 h-full px-3 text-book-muted hover:text-book-brown"
            onClick={() => togglePasswordVisibility('current')}
          >
            {showCurrentPassword ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </Button>
        </div>
        {errors.current_password && (
          <p className="text-sm text-red-500">{errors.current_password.message}</p>
        )}
      </div>

      {/* New Password */}
      <div className="space-y-2">
        <Label htmlFor="new_password" className="text-book-brown">
          <Lock className="w-4 h-4 inline mr-2" />
          Nowe hasło
        </Label>
        <div className="relative">
          <Input
            id="new_password"
            type={showNewPassword ? 'text' : 'password'}
            {...register('new_password')}
            className={errors.new_password ? 'border-red-500 pr-10' : 'pr-10'}
            disabled={isLoading}
            placeholder="Wprowadź nowe hasło"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-0 top-0 h-full px-3 text-book-muted hover:text-book-brown"
            onClick={() => togglePasswordVisibility('new')}
          >
            {showNewPassword ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </Button>
        </div>
        {errors.new_password && (
          <p className="text-sm text-red-500">{errors.new_password.message}</p>
        )}
        <ul className="text-xs text-book-muted space-y-1 mt-2">
          <li>• Minimum 8 znaków</li>
          <li>• Co najmniej jedna wielka litera</li>
          <li>• Co najmniej jedna mała litera</li>
          <li>• Co najmniej jedna cyfra</li>
        </ul>
      </div>

      {/* Confirm Password */}
      <div className="space-y-2">
        <Label htmlFor="confirm_password" className="text-book-brown">
          <Lock className="w-4 h-4 inline mr-2" />
          Potwierdź nowe hasło
        </Label>
        <div className="relative">
          <Input
            id="confirm_password"
            type={showConfirmPassword ? 'text' : 'password'}
            {...register('confirm_password')}
            className={errors.confirm_password ? 'border-red-500 pr-10' : 'pr-10'}
            disabled={isLoading}
            placeholder="Powtórz nowe hasło"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-0 top-0 h-full px-3 text-book-muted hover:text-book-brown"
            onClick={() => togglePasswordVisibility('confirm')}
          >
            {showConfirmPassword ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </Button>
        </div>
        {errors.confirm_password && (
          <p className="text-sm text-red-500">{errors.confirm_password.message}</p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4 pt-4">
        <Button
          type="submit"
          className="bg-book-gold hover:bg-book-gold-hover"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Zmienianie hasła...
            </>
          ) : (
            'Zmień hasło'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => reset()}
          disabled={isLoading}
        >
          Wyczyść
        </Button>
      </div>
    </form>
  );
}
